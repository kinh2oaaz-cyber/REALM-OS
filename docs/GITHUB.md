# Publishing REALM OS on GitHub

## Before you launch
1. **No secrets.** Confirm `.gitignore` covers `.env`, tokens, `*.key`,
   `*.pem`, `*.db`, `logs/`, `__pycache__`, `.venv`, `dist`, `build`.
2. **Never commit pasted tokens.** Anything pasted into chat/commits is
   public; **rotate/revoke** it. (A random string before `python main.py`
   in your message was **not** used and is **not** stored in this repo.)
3. **Data dir** is `%LOCALAPPDATA%\REALM OS`, outside the repo.
4. **License** — default is proprietary `LICENSE`; switch to
   MIT/Apache-2.0/GPL-3.0 if you want public reuse; keep Tabler (MIT) /
   PySide6 / psutil / cryptography notices.
5. **Logo** `REALM OS LOGO.png` is committed; ensure you own it.
6. **CI** `.github/workflows/tests.yml` runs tests on `windows-latest`.

## Create repo + first push (PowerShell)
```powershell
Set-Location "C:\work station\REALM OS"
git init
git branch -M main
git add .
git status                      # verify no .db/.log/.env/__pycache__/dist
git commit -m "REALM OS v1.0.0"
git remote add origin https://github.com/<you>/realm-os.git
# authenticate with YOUR credential manager or `gh auth login`. Do NOT paste a token in chat.
git push -u origin main
```

## With GitHub CLI (recommended; no pasted token)
```powershell
gh auth login                   # interactive, stores token in OS keychain
gh repo create realm-os --private --source=. --remote=origin --push
```

## Update later
```powershell
git add .
git commit -m "..."
git push
```

## Hygiene check before pushing
```powershell
git check-ignore .env realmos.db logs __pycache__ .venv dist
git ls-files | Select-String -Pattern '\.db$|\.log$|__pycache__|\.venv|\.env$'   # should print nothing
```

## Releases / packaging
See `scripts/build-windows.ps1` + `packaging/realmos.spec`
(`dist/REALM OS.exe`, icon, QtMultimedia/QtPdf, `REALM OS LOGO.png`).
Attach `dist` artifacts to a GitHub Release; never commit `dist/`.
