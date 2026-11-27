## Summary
What changed and why.

## Checklist
- [ ] `python -m unittest discover -s tests -t .` passes
- [ ] `python -m compileall` clean
- [ ] No secrets / no `.env` / no `*.db` / no `__pycache__` committed
- [ ] No fake/placeholder buttons; real functionality
- [ ] Preserves existing working functionality; didn't overwrite unrelated files
- [ ] Additive DB migration if schema changed
