# 📝 Forge Notes & Roadmap

_Last updated: Aug 29, 2025_

---

## 🔥 Progress So Far
- API live and responding on Railway
- `/v2/optimise` + `/v2/analyse` sealed workshop routes added
- `/health` + `/version` endpoints working
- Safety layer patched (NSFW opt-in, youth tokens handled)
- Profiles integrated (`allow_nsfw` respected)
- Image analysis upgraded 🔬 supports `basic`, `detailed`, `tags`
- CI/CD drafted:
  - `lint.yml` for code style
  - `test.yml` for smoke tests on endpoints
- Reference spec available at [`docs/forge_master_spec.md`](docs/forge_master_spec.md)

---

## 🚀 To-Do (Next Session)

1. **Fix optimisation bug**
   - Error: `list index out of range` in `/v2/optimise`
   - Inspect `forge/prompts.py:build_prompts` + handling of empty/cleaned prompts.

2. **Verify analysis modes**
   - Run `/v2/analyse` with:
      - `"basic"`
      - `"detailed"`
      - `"tags"`
   - Confirm consistent outputs.

3. **CI/CD integration**
   - Push `.github/workflows/lint.yml` + `.github/workflows/test.yml`
   - Confirm pipelines trigger on PRs.

4. **Add minimal unit + integration tests**
   - Use pytest + schemathesis
   - Cover `/health`, `/version`, `/v2/optimise`, `/v2/analyse`.

5. **Stable deployment**
   - Confirm Railway redeploy runs clean.
   - Validate endpoints via curl.

6. **Stretch goals**
   - Add `/docs` endpoint 📖 auto-serve OpenAPI schema or docs
   - More profiles (e.g. cinematic, fantasy presets)

---

## 📌 Notes
- Keep `allow_nsfw` optional (default = false) for Forge safety policy.
- Prompt packages remain **engineered specs** → Forge does not generate final media, only blueprints.
- CI ensures no broken builds enter `main`.

---

**Created by Resist 🔨🔥**  
Contact: [@ResistAiArt](https://x.com/ResistAiArt)
