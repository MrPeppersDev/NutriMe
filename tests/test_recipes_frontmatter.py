"""S9 frontmatter builder + YAML emit/parse round-trip."""

import pytest

from nutrime.recipes.frontmatter import (
    Attribution,
    OPTIONAL_FIELDS,
    REQUIRED_FIELDS,
    Yields,
    build_recipe_frontmatter,
    emit_yaml,
    parse_frontmatter,
    render_markdown_document,
    split_markdown_document,
    validate_frontmatter,
)


def _minimal_attribution() -> Attribution:
    return Attribution(
        source_name="TestSource",
        source_url="https://example.com/r/1",
        source_license="test-license",
        ingested_at="2026-07-02T12:00:00Z",
        ingestion_method="unit_test",
    )


def _minimal_frontmatter() -> dict:
    return build_recipe_frontmatter(
        recipe_id="rcp-test",
        title="Test Recipe",
        attribution=_minimal_attribution(),
        source_status="live",
        last_source_check_at="2026-07-02T12:00:00Z",
        yields=Yields(count=4),
        top_allergens_present=[],
    )


class TestAttributionArchivalField:
    def test_snapshot_url_included_when_set(self) -> None:
        attribution = Attribution(
            source_name="X",
            source_url="https://original.example/r/1",
            source_license="PD",
            ingested_at="2026-07-07T00:00:00Z",
            ingestion_method="test",
            archived_snapshot_url="https://web.archive.org/web/1id_/x",
        )
        out = attribution.as_dict()
        assert out["archived_snapshot_url"] == (
            "https://web.archive.org/web/1id_/x"
        )

    def test_snapshot_url_absent_by_default(self) -> None:
        assert "archived_snapshot_url" not in _minimal_attribution().as_dict()


class TestBuildRecipeFrontmatter:
    def test_all_s9_required_fields_populated(self) -> None:
        fm = _minimal_frontmatter()
        for field in REQUIRED_FIELDS:
            assert field in fm, f"missing S9 required field {field!r}"

    def test_defaults_are_sensible(self) -> None:
        fm = _minimal_frontmatter()
        assert fm["content_type"] == "recipe"
        assert fm["version"] == "1.0.0"
        assert fm["source_removed_at"] is None
        assert fm["material_implication_note"] is None
        assert fm["modality_availability"] == ["text"]
        assert fm["ingredient_resolution_status"] == "unresolved_pending_review"
        assert fm["ingredient_resolution_summary"] == {
            "fully_resolved": 0, "partial": 0, "unresolved": 0
        }

    def test_yields_dict_shape(self) -> None:
        fm = build_recipe_frontmatter(
            recipe_id="rcp-x",
            title="X",
            attribution=_minimal_attribution(),
            source_status="live",
            last_source_check_at="2026-07-02T12:00:00Z",
            yields=Yields(count=6, unit="servings", yield_note="serves 6 as main"),
            top_allergens_present=[],
        )
        assert fm["yields"] == {
            "count": 6, "unit": "servings", "yield_note": "serves 6 as main"
        }

    def test_rejects_bad_source_status(self) -> None:
        with pytest.raises(ValueError):
            build_recipe_frontmatter(
                recipe_id="rcp-x",
                title="X",
                attribution=_minimal_attribution(),
                source_status="ok",  # invalid
                last_source_check_at="2026-07-02T12:00:00Z",
                yields=Yields(count=4),
                top_allergens_present=[],
            )

    def test_rejects_bad_resolution_status(self) -> None:
        with pytest.raises(ValueError):
            build_recipe_frontmatter(
                recipe_id="rcp-x",
                title="X",
                attribution=_minimal_attribution(),
                source_status="live",
                last_source_check_at="2026-07-02T12:00:00Z",
                yields=Yields(count=4),
                top_allergens_present=[],
                ingredient_resolution_status="totally_resolved",  # invalid
            )


class TestValidateFrontmatter:
    def test_valid_passes(self) -> None:
        validate_frontmatter(_minimal_frontmatter())

    def test_missing_required_raises(self) -> None:
        fm = _minimal_frontmatter()
        del fm["yields"]
        with pytest.raises(ValueError, match="yields"):
            validate_frontmatter(fm)

    def test_wrong_content_type_raises(self) -> None:
        fm = _minimal_frontmatter()
        fm["content_type"] = "education"
        with pytest.raises(ValueError, match="content_type"):
            validate_frontmatter(fm)

    def test_optional_fields_are_documented(self) -> None:
        # Sanity: the S9 optional field set is exposed for downstream tooling
        assert set(OPTIONAL_FIELDS) == {
            "cooking_technique_tags",
            "pairing_role_summary",
            "equipment_required",
            "seasonality_tags",
            "regional_origin",
            "historical_context_note",
            "editor_notes",
            "image_references",
        }


class TestYamlRoundTrip:
    def test_scalars_round_trip(self) -> None:
        data = {
            "s": "hello",
            "n": 42,
            "f": 1.5,
            "t": True,
            "u": False,
            "z": None,
        }
        yaml = emit_yaml(data)
        parsed = parse_frontmatter(yaml)
        assert parsed == data

    def test_string_with_single_quote(self) -> None:
        data = {"note": "it's a test"}
        parsed = parse_frontmatter(emit_yaml(data))
        assert parsed == data

    def test_flat_list_round_trip(self) -> None:
        data = {"tags": ["a", "b", "c"]}
        parsed = parse_frontmatter(emit_yaml(data))
        assert parsed == data

    def test_empty_list(self) -> None:
        data = {"tags": []}
        parsed = parse_frontmatter(emit_yaml(data))
        assert parsed == data

    def test_nested_dict_round_trip(self) -> None:
        data = {"y": {"count": 4, "unit": "servings"}}
        parsed = parse_frontmatter(emit_yaml(data))
        assert parsed == data

    def test_recipe_frontmatter_round_trip(self) -> None:
        fm = _minimal_frontmatter()
        text = emit_yaml(fm)
        parsed = parse_frontmatter(text)
        assert parsed == fm


class TestRenderMarkdownDocument:
    def test_render_split_round_trip(self) -> None:
        fm = _minimal_frontmatter()
        body = ">> title: Test Recipe\n\n-- Ingredients\n\n@salt\n"
        document = render_markdown_document(fm, body)
        assert document.startswith("---\n")
        assert "\n---\n" in document
        recovered_fm, recovered_body = split_markdown_document(document)
        assert recovered_fm == fm
        assert recovered_body.rstrip() == body.rstrip()

    def test_render_validates(self) -> None:
        fm = _minimal_frontmatter()
        del fm["title"]
        with pytest.raises(ValueError):
            render_markdown_document(fm, "body")

    def test_split_rejects_missing_fence(self) -> None:
        with pytest.raises(ValueError):
            split_markdown_document("no fence at all")
