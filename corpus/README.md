# Corpus snapshot

Repo copy of the recipe corpus vault (markdown source-of-truth, S9 Q9.1) so
another machine can pull it down without re-ingesting. The historical
cookbook collection (Project Gutenberg Bookshelf 419, `gutenberg_text_v1`,
~2,600 files) is deliberately excluded — it is opt-in-only in the app and
re-ingestable via `nutrime recipes` ingest commands if ever wanted.

Contents (2,218 recipes):

- `themealdb_api_v1` — 790 (TheMealDB free tier, attribution required)
- `schema_org_jsonld_v1` — 725 (saved-pins URL ingest)
- `myplate_wayback_html_v1` — 649 (USDA MyPlate Kitchen)
- `nhlbi_html_v1` — 54 (NHLBI heart-healthy)

To seed a fresh install, copy into the data dir the app reads
(`~/.nutrime` by default, or `$NUTRIME_DATA_DIR`):

```sh
mkdir -p ~/.nutrime/corpus
cp -R corpus/recipes ~/.nutrime/corpus/
```

This is a snapshot, not a live mount — the app reads/writes only the data
dir, so re-sync here when the vault changes materially.
