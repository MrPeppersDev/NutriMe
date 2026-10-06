"""Household members (issue #29) — per-member identity on one shared device.

A tenant is a household; a member is a person in it. Personal state
(intake profile, screener responses, feedback atoms, consent decisions)
is keyed by ``member_id``; the recipe corpus, inventory and plans stay
household-shared. Household constraints are the union of every active
member's avoids/prefers, through the existing abstracted-constraint seam
(Tension #5: constraint-only sharing, no raw data exposure).

No auth yet: the web surface offers a picker, not a login.

Members are archived, never deleted — atoms keep a resolvable subject
and the record stays honest about who said what.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from nutrime.knowledge.ids import uuid7
from nutrime.tenancy import _now_iso

DEFAULT_MEMBER_NAME = "Me"


class MemberError(ValueError):
    """Unknown, archived, or otherwise unusable member reference."""


@dataclass(frozen=True)
class Member:
    id: str
    display_name: str
    status: str
    created_at: str

    @property
    def active(self) -> bool:
        return self.status == "active"


def new_member_id() -> str:
    return f"mem-{uuid7()}"


def _clean_name(display_name: str) -> str:
    name = " ".join((display_name or "").split())
    if not 1 <= len(name) <= 60:
        raise MemberError("member name must be 1-60 characters")
    return name


def add_member(
    conn: sqlite3.Connection, tenant_id: str, display_name: str
) -> Member:
    name = _clean_name(display_name)
    taken = {
        m.display_name.casefold() for m in list_members(conn, tenant_id)
    }
    if name.casefold() in taken:
        raise MemberError(f"a member named {name!r} already exists")
    member = Member(
        id=new_member_id(),
        display_name=name,
        status="active",
        created_at=_now_iso(),
    )
    conn.execute(
        "INSERT INTO member (id, tenant_id, display_name, status, created_at)"
        " VALUES (?, ?, ?, 'active', ?)",
        (member.id, tenant_id, member.display_name, member.created_at),
    )
    conn.commit()
    return member


def list_members(
    conn: sqlite3.Connection, tenant_id: str, *, include_archived: bool = False
) -> list[Member]:
    sql = (
        "SELECT id, display_name, status, created_at FROM member"
        " WHERE tenant_id = ?"
    )
    if not include_archived:
        sql += " AND status = 'active'"
    sql += " ORDER BY created_at, id"
    return [Member(*row) for row in conn.execute(sql, (tenant_id,))]


def get_member(
    conn: sqlite3.Connection, tenant_id: str, member_id: str
) -> Member:
    """Resolve an active member of this household or raise MemberError."""
    row = conn.execute(
        "SELECT id, display_name, status, created_at FROM member"
        " WHERE tenant_id = ? AND id = ?",
        (tenant_id, member_id),
    ).fetchone()
    if row is None:
        raise MemberError(f"no member {member_id!r} in this household")
    member = Member(*row)
    if not member.active:
        raise MemberError(f"member {member.display_name!r} is archived")
    return member


def rename_member(
    conn: sqlite3.Connection, tenant_id: str, member_id: str, display_name: str
) -> Member:
    member = get_member(conn, tenant_id, member_id)
    name = _clean_name(display_name)
    others = {
        m.display_name.casefold()
        for m in list_members(conn, tenant_id)
        if m.id != member.id
    }
    if name.casefold() in others:
        raise MemberError(f"a member named {name!r} already exists")
    conn.execute(
        "UPDATE member SET display_name = ? WHERE tenant_id = ? AND id = ?",
        (name, tenant_id, member.id),
    )
    conn.commit()
    return Member(member.id, name, member.status, member.created_at)


def archive_member(
    conn: sqlite3.Connection, tenant_id: str, member_id: str
) -> None:
    get_member(conn, tenant_id, member_id)
    if len(list_members(conn, tenant_id)) <= 1:
        raise MemberError("a household needs at least one active member")
    conn.execute(
        "UPDATE member SET status = 'archived', archived_at = ?"
        " WHERE tenant_id = ? AND id = ?",
        (_now_iso(), tenant_id, member_id),
    )
    conn.commit()


def default_member_id(conn: sqlite3.Connection, tenant_id: str) -> str:
    """The household's first active member — what member-unaware callers
    (CLI without --member, pre-picker web requests) act as."""
    members = list_members(conn, tenant_id)
    if not members:
        raise MemberError("household has no active members")
    return members[0].id


def bootstrap_default_member(conn: sqlite3.Connection, tenant_id: str) -> str:
    """Idempotent (called from app.initialize).

    Every household gets one member. On the first run after migration
    0006, the legacy single ``intake_profile`` row and any member-less
    screener responses move under that member — exactly once, because the
    copy only runs when the member is created.
    """
    existing = founding_member_id(conn, tenant_id)
    if existing is not None:
        return existing
    member = add_member(conn, tenant_id, DEFAULT_MEMBER_NAME)
    conn.execute(
        """
        INSERT INTO intake_profile_v2 (
            tenant_id, member_id, year_of_birth, sex_assigned_at_birth,
            height_cm, weight_kg, life_stage,
            dietary_preferences, allergens, created_at, updated_at
        )
        SELECT tenant_id, ?, year_of_birth, sex_assigned_at_birth,
               height_cm, weight_kg, life_stage,
               dietary_preferences, allergens, created_at, updated_at
        FROM intake_profile WHERE tenant_id = ?
        """,
        (member.id, tenant_id),
    )
    conn.execute(
        "UPDATE intake_screener_response SET member_id = ?"
        " WHERE tenant_id = ? AND member_id IS NULL",
        (member.id, tenant_id),
    )
    conn.commit()
    return member.id


def founding_member_id(conn: sqlite3.Connection, tenant_id: str) -> str | None:
    """The member bootstrap created (archived or not)."""
    row = conn.execute(
        "SELECT id FROM member WHERE tenant_id = ? ORDER BY created_at, id",
        (tenant_id,),
    ).fetchone()
    return row[0] if row else None


def subject_ids_for(
    conn: sqlite3.Connection, tenant_id: str, member_id: str
) -> tuple[str, ...]:
    """Atom subject ids that belong to this member. Atoms written before
    #29 carry ``subject_id = tenant_id``; they belong to the founding
    member."""
    if member_id == founding_member_id(conn, tenant_id):
        return (member_id, tenant_id)
    return (member_id,)
