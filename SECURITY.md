# Security

REALM OS is **local-first**. Your data stays in a per-user SQLite
database under `%LOCALAPPDATA%\REALM OS`. No telemetry is sent. The only
network use is by features that inherently need it (Network Monitor
checks, optional Weather, optional local AI via Ollama); nothing is
exfiltrated.

## Reporting a vulnerability
Please open a private security advisory on GitHub or contact the
maintainer. Do not file public issues with exploit details.

## Secrets
- **Never commit secrets** (tokens, keys, passwords, `.env`, `*.key`,
  `*.pem`, databases, logs). `.gitignore` excludes them.
- If you accidentally paste a token anywhere (chat, commit, issue),
  **rotate/revoke it immediately**. REALM OS does not store API keys.
- Password-protected notes and the Password Vault encrypt at rest with
  `cryptography` Fernet + PBKDF2-HMAC-SHA256; passwords are never logged
  or stored in plaintext. Master password is not persisted.
- The local model (REALM AI) runs on `127.0.0.1` (Ollama); no cloud AI.
