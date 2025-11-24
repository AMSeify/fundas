# 🚀 Quick Release Checklist

## First-Time Setup (One-time only)

- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Set up Trusted Publishing on PyPI:
  - Account Settings → Publishing → Add new pending publisher
  - Project: `fundas`, Owner: `AMSeify`, Repo: `fundas`
  - Workflow: `publish.yml`, Environment: `pypi`
- [ ] Push code to GitHub

## For Every Release

### 1. Pre-Release Validation
```bash
# Optional: Run validation script
python scripts/validate_release.py

# Or manually:
pytest tests/ --cov=fundas
black --check fundas/ tests/
flake8 fundas/ tests/ --max-line-length=88 --extend-ignore=E203
python -m build && twine check dist/*
```

### 2. Update Version
Edit `fundas/__init__.py`:
```python
__version__ = "X.Y.Z"  # Update this
```

### 3. Commit and Tag
```bash
git add fundas/__init__.py
git commit -m "Bump version to X.Y.Z"
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 4. Create GitHub Release
1. Go to https://github.com/AMSeify/fundas/releases
2. Click "Draft a new release"
3. Choose tag `vX.Y.Z`
4. Add release title: `vX.Y.Z - Release Name`
5. Add release notes:
   ```
   ## New Features
   - Feature 1
   - Feature 2
   
   ## Bug Fixes
   - Fix 1
   - Fix 2
   
   ## Breaking Changes (if any)
   - Change 1
   ```
6. Click "Publish release"

### 5. Monitor
- [ ] Watch GitHub Actions workflow complete
- [ ] Check PyPI page: https://pypi.org/project/fundas/
- [ ] Test install: `pip install fundas==X.Y.Z`
- [ ] Verify: `python -c "import fundas; print(fundas.__version__)"`

## Version Bumping Guide

| Change Type | Example | When to Use |
|-------------|---------|-------------|
| Patch (0.0.X) | 0.1.0 → 0.1.1 | Bug fixes only |
| Minor (0.X.0) | 0.1.0 → 0.2.0 | New features (backwards-compatible) |
| Major (X.0.0) | 0.9.0 → 1.0.0 | Breaking changes or first stable |

## Common Issues

### "Package name already exists"
→ Change `name` in `pyproject.toml` to something unique

### "Trusted publisher not configured"
→ Double-check PyPI settings, wait a few minutes, try again

### Tests failing
→ Fix locally first: `pytest tests/`

### Wrong version published
→ Can't unpublish, must bump to next version

## Quick Commands

```bash
# Run all tests
pytest tests/ --cov=fundas

# Format code
black fundas/ tests/

# Check formatting
black --check fundas/ tests/

# Lint
flake8 fundas/ tests/ --max-line-length=88 --extend-ignore=E203

# Build package
python -m build

# Check build
twine check dist/*

# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# View current version
python -c "import fundas; print(fundas.__version__)"
```

## Files You Need to Update for Each Release

✏️ **Only one file**: `fundas/__init__.py` (update `__version__`)

Everything else is automated! 🎉
