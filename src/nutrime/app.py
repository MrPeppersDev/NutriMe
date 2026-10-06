"""Application bootstrap — open both DBs, run migrations, ensure tenant.

The deployment shell's role per Stage 6 step 1: a single ``initialize()`` entry
point that opens substrate + operational SQLite databases under the data
directory, applies any pending migrations on each, and bootstraps the single
tenant (F9 Q2 — locally-generated UUID at first install). Returns an
:class:`Application` carrying the live connections plus the resolved tenant id
for downstream callers (CLI, future server process, tests).

The two databases are tracked independently per S12 — each owns its own
``schema_migrations`` table — so migrations on one cannot stall the other.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from nutrime.audit import AuditLog, attach_pre_egress_audit
from nutrime.db import apply_migrations, connect
from nutrime.paths import (
    default_corpus_dir,
    default_data_dir,
    default_operational_migrations_dir,
    default_substrate_migrations_dir,
)
from nutrime.llm.phi import register_llm_envelopes
from nutrime.phi import PhiEnvelopeRegistry, default_phi_envelope_registry
from nutrime.recipes.phi import register_recipe_envelopes
from nutrime.rules import RuleEngine, default_rule_engine
from nutrime.tenancy import bootstrap_tenant


@dataclass
class Application:
    substrate: sqlite3.Connection
    operational: sqlite3.Connection
    tenant_id: str
    data_dir: Path
    corpus_dir: Path
    rule_engine: RuleEngine
    phi_envelope: PhiEnvelopeRegistry
    audit: AuditLog

    @property
    def default_member_id(self) -> str:
        from nutrime.members import default_member_id

        return default_member_id(self.substrate, self.tenant_id)


def initialize(
    data_dir: Path | None = None,
    *,
    substrate_migrations: Path | None = None,
    operational_migrations: Path | None = None,
    tenant_name: str = "Default Household",
    phi_envelope: PhiEnvelopeRegistry | None = None,
    rule_engine: RuleEngine | None = None,
) -> Application:
    data_dir = data_dir or default_data_dir()
    substrate_migrations = substrate_migrations or default_substrate_migrations_dir()
    operational_migrations = (
        operational_migrations or default_operational_migrations_dir()
    )

    data_dir.mkdir(parents=True, exist_ok=True)

    corpus_dir = default_corpus_dir(data_dir)
    (corpus_dir / "recipes").mkdir(parents=True, exist_ok=True)
    (corpus_dir / "plans").mkdir(parents=True, exist_ok=True)

    substrate = connect(data_dir / "substrate.db")
    apply_migrations(substrate, substrate_migrations)

    operational = connect(data_dir / "operational.db")
    apply_migrations(operational, operational_migrations)

    tenant_id = bootstrap_tenant(substrate, name=tenant_name)

    # Household members (#29): every install has at least one; the legacy
    # single profile moves under it on first run after migration 0006.
    from nutrime.members import bootstrap_default_member

    bootstrap_default_member(substrate, tenant_id)

    audit = AuditLog(operational)
    audit.ensure_tenant_created(tenant_id)

    # Consent baseline (#21): idempotent; grants local_operation
    # (retroactive over pre-#21 captures) and stores explicit declines
    # for publication purposes so fail-closed is a recorded decision.
    from nutrime.consent import bootstrap_baseline

    bootstrap_baseline(substrate, tenant_id)

    phi_envelope = phi_envelope or default_phi_envelope_registry()
    register_recipe_envelopes(phi_envelope)
    register_llm_envelopes(phi_envelope)

    engine = rule_engine or default_rule_engine(phi_envelope)
    attach_pre_egress_audit(engine, audit)

    return Application(
        substrate=substrate,
        operational=operational,
        tenant_id=tenant_id,
        data_dir=data_dir,
        corpus_dir=corpus_dir,
        rule_engine=engine,
        phi_envelope=phi_envelope,
        audit=audit,
    )
