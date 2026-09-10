# Development TODO

> **Last Updated:** 2026-09-10

## Immediate Gaps (from repo-state sync)
- [ ] Re-add missing `docker-compose.yml` (or correct sprint/Changelog 0.3.2 history)
- [ ] Re-scaffold `tests/` suite (27-test baseline claimed, dir absent)
- [ ] Export `register_client_recognition_tool` + `register_department_tool` from `tools/__init__.py`
- [ ] Bump `pyproject.toml` version `0.1.0` → `0.3.3`
- [ ] Resolve `greet_user` / `Greeting Tool.md` vs missing `tools/greeting.py` (no references in `src/`)
- [ ] Refresh `README.md`: route prefixes (`/tools/call`, `/dev/*`), 6 tool names, repo layout (`department_list.py`, `client_recognition.py`)

## Planned Enhancements

### Phase 2: Telephony & Call Tools
- [ ] Implement `trigger_outbound_call` in `tools/calls.py` calling `LktClient.trigger_outbound_call`
- [ ] Implement `get_call_status` for querying call status by `call_id`
- [ ] Implement `get_active_calls` for inspecting active Redis / LiveKit sessions
- [ ] Implement `end_active_call` for disconnecting ongoing calls

### Phase 3: Knowledge Base Tools
- [ ] Implement `search_kb` for executing hybrid full-text and semantic queries
- [ ] Implement `ingest_kb_document` for adding documents, text, and URLs
- [ ] Implement `list_kb_collections` for listing org-specific documents

### Phase 4: Analytics & SIP Management
- [ ] Implement `get_call_metrics` (answer rate, duration, call outcomes)
- [ ] Implement `search_call_logs` with pagination and filters
- [ ] Implement `list_sip_trunks` and `setup_inbound_sip`
- [ ] Implement `get_org_config` and `update_org_config`
