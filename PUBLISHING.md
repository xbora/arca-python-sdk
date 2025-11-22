# Publishing to PyPI

This guide shows you how to publish the Arca SDK to PyPI so users can install it with `pip install arca`.

## Prerequisites

1. **Create a PyPI account**: https://pypi.org/account/register/
2. **Create an API token**: https://pypi.org/manage/account/token/
   - Give it a name like "arca-sdk-upload"
   - Scope: "Entire account" (for first upload)
   - Save the token securely!

## One-Time Setup

Install the publishing tools:

```bash
pip install build twine
```

## Publishing Steps

### 1. Update Version (if needed)

Edit `arca/version.py`:
```python
__version__ = '0.1.1'  # Increment as needed
```

### 2. Build the Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new distribution files
python -m build
```

This creates two files in `dist/`:
- `arca-0.1.0.tar.gz` (source distribution)
- `arca-0.1.0-py3-none-any.whl` (wheel distribution)

### 3. Check the Package (Optional but Recommended)

```bash
twine check dist/*
```

### 4. Upload to Test PyPI (Optional but Recommended)

Test first to make sure everything works:

```bash
# Upload to test PyPI
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (including the `pypi-` prefix)

Then test installing from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ arca
```

### 5. Upload to Production PyPI

Once you're confident it works:

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token

### 6. Verify Installation

After a few minutes, anyone can install:

```bash
pip install arca
```

## Configuration File Method (Easier)

Create `~/.pypirc` to avoid entering credentials each time:

```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

Then you can just run:
```bash
twine upload dist/*
```

## Updating the Package

When you make changes:

1. Update version in `arca/version.py`
2. Commit and push to GitHub
3. Build: `python -m build`
4. Upload: `twine upload dist/*`

## Common Issues

**"File already exists"**: You can't re-upload the same version. Increment the version number.

**"Invalid credentials"**: Make sure you're using `__token__` as username and your full API token as password.

**Import errors after install**: Make sure your `__init__.py` exports are correct and you're using `find_packages()` in setup.py.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `0.1.0` → `0.1.1` (bug fixes)
- `0.1.0` → `0.2.0` (new features, backward compatible)
- `0.1.0` → `1.0.0` (major changes, may break compatibility)
