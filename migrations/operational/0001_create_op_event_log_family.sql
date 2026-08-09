-- Operational baseline, event-log family (schema.md S8 Q8.3).
-- Lands with Stage 6 sub-commit 5.1 (issue #22): audit persistence must exist
-- before the first LLM egress; audit history cannot be backfilled.
--
-- Two-layer pattern per Q8.1: these are the heavy operational counterparts to
-- lighter substrate atoms (audit_log_entry / phi_crossing_event), correlated
-- via request_id. Remaining S8 families (session/state, cycle-state,
-- op_job_queue) land with the components that consume them.

-- 1. LLM request log
CREATE TABLE op_llm_request_log (
  id                       TEXT PRIMARY KEY,            -- llr-{uuidv7}
  request_id               TEXT NOT NULL,               -- correlates to substrate phi_crossing_event.request_id + verification_results.llm_request_id
  llm_provider             TEXT NOT NULL,
  llm_model                TEXT NOT NULL,
  request_payload_hash     TEXT NOT NULL,               -- SHA-256 of full request payload
  request_payload          TEXT,                        -- full payload if under size threshold; NULL if hash-only (build-time threshold)
  response_payload         TEXT,
  response_payload_hash    TEXT NOT NULL,
  prompt_tokens            INTEGER,
  completion_tokens        INTEGER,
  total_cost_usd           REAL,                        -- approximate; informs cost transparency per Q7.5.b
  latency_ms               INTEGER,
  retry_attempts           INTEGER NOT NULL DEFAULT 0,
  outcome                  TEXT NOT NULL,
  error_detail             TEXT,
  phi_categories           TEXT NOT NULL,               -- per Q8.2.e defense-in-depth
  caller_context           TEXT NOT NULL,               -- 'intake_agent' | 'verification' | 'inference_synthesis' | 'dre_extraction' | etc.
  started_at               TEXT NOT NULL,
  completed_at             TEXT,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (outcome IN ('success','error_provider','error_timeout','error_rate_limit','error_validation')),
  CHECK (phi_categories = '[]')                          -- defense-in-depth: cloud LLM calls never carry PHI
);

CREATE INDEX idx_llr_request_id    ON op_llm_request_log(request_id);
CREATE INDEX idx_llr_caller_time   ON op_llm_request_log(caller_context, started_at DESC);
CREATE INDEX idx_llr_outcome       ON op_llm_request_log(outcome, started_at) WHERE outcome != 'success';
CREATE INDEX idx_llr_provider_time ON op_llm_request_log(llm_provider, started_at DESC);

-- 2. Collapsed event log (audit + epistemic-trail + system events)
CREATE TABLE op_event_log (
  id                       TEXT PRIMARY KEY,            -- evt-{uuidv7}
  event_kind               TEXT NOT NULL,               -- 'audit' | 'epistemic_trail' | 'system'
  event_subkind            TEXT,                        -- per-kind discriminator (e.g., 'data_write', 'consent_change', 'reasoning_step', 'orchestration_handoff')
  request_id               TEXT,                        -- correlation to op_llm_request_log + substrate audit_log_entry
  parent_event_id          TEXT,                        -- FK to op_event_log.id; lets epistemic-trail chains form trees
  subject_id               TEXT,                        -- substrate record this event is about (loose polymorphic per S4/S5/S6)
  subject_type             TEXT,                        -- 'atom' | 'molecule' | 'synthesized' | 'relationship' | NULL for non-record events
  actor                    TEXT NOT NULL,               -- 'user' | 'system' | 'agent_id' | 'job_id' | etc.
  payload                  TEXT NOT NULL,               -- JSON; event-kind/subkind-specific shape per schema-of-schemas
  phi_categories           TEXT NOT NULL,               -- documents routing concern; no CHECK (events legitimately carry PHI when about PHI-bearing records)
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (event_kind IN ('audit','epistemic_trail','system')),
  CHECK (subject_type IN ('atom','molecule','synthesized','relationship') OR subject_type IS NULL)
);

CREATE INDEX idx_evt_request_id    ON op_event_log(request_id);
CREATE INDEX idx_evt_subject       ON op_event_log(subject_id, subject_type, recorded_at DESC);
CREATE INDEX idx_evt_kind_time     ON op_event_log(event_kind, recorded_at DESC);
CREATE INDEX idx_evt_parent        ON op_event_log(parent_event_id) WHERE parent_event_id IS NOT NULL;
