# GitHub security checklist (REALM OS)

Goal: publish only what's needed to **use / build / contribute** REALM OS.
**No internal security secrets, no user data.**

## Verified clean
- [x] No tokens/keys/passwords committed. Scan `ghp_|gho_|github_pat_|AKIA|glpat-|xox*|-----BEGIN *PRIVATE KEY-----|Bearer`.
- [x] No pasted strings in repo. No `.env`. `.env.example` only.
- [x] No `*.db/*.sqlite`, `*.log`, `*.key`, `*.pem`, `*.pfx`, `*.p12`, `secrets/`.
- [x] No `__pycache__`, `.venv`, `dist/`, `build/`, `*.egg-info`.
- [x] No runtime data: app data is `%LOCALAPPDATA%\REALM OS`, outside repo; `REALMOS_DATA_DIR`.
- [x] `gitignore`, `.gitattributes`, `.editorconfig`.
- [x] `SECURITY.md`, `LICENSE`, `CONTRIBUTING.md`, `docs/GITHUB.md`, `docs/PACKAGING.md`.
- [x] `.github/workflows/tests.yml` (offscreen, temp data dir; no secrets).
- [x] Password-protected notes + Password Vault encrypt at rest; passwords not logged/stored; master password not persisted. No secrets in logs.
- [x] REALM AI local (Ollama `127.0.0.1`); no cloud AI key. No telemetry.
- [x] `REALM OS LOGO.png` + `.ico` (owned asset), Tabler Icons MIT license bundled.

## Committed = only what's needed
`app/`, `core/`, `database/`, `modules/`, `system/`, `ui/`, `security/`
(source only), `integrations/`, `assets/`, `tests/`, `docs/`,
`scripts/`, `packaging/`, `.github/`, `README`, `LICENSE`, packaging
config, `REALM OS LOGO.*`.

## Not committed
secrets, `.env`, `*.db`, `*.log`, `logs/`, `__pycache__`, `.venv`,
`dist/`, `build/`, `*.key`, `*.pem`, generated `_screenshot`,
`background_redgold_v*.png` (regenerated at runtime).

## Push safely
```powershell
# authenticate YOURSELF. Never paste a token in chat/commits.
gh auth login                      # stores token in OS keychain
git push -u origin main            # remote already = https://github.com/kinh2oaaz-cyber/REALM-OS.git
```
Pre-push hygiene:
```powershell
git check-ignore .env realmos.db logs __pycache__ .venv dist secrets
git ls-files | Select-String -Pattern '\.db$|\.log$|__pycache__|\.venv|^dist/|^build/|\.env$|secrets'
git grep -nE 'ghp_|gho_|github_pat_|AKIA|BEGIN [A-Z ]*PRIVATE KEY'
```

## If you accidentally committed a secret
Rotate/revoke it immediately, `git rm`, recommit, and rewrite history
(`git filter-repo` / BFG); GitHub secret scanning + `SECURITY.md`.

## Advertising
Safe to share repo. No internal secrets. **Code-sign** the exe for
public distribution; `dist/` not committed. Review `LICENSE`.
