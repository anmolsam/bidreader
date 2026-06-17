#!/usr/bin/env bash
# Safe release: build, verify, and publish bidreader to PyPI.
#
#   export PYPI_TOKEN=pypi-...        # project-scoped token; NEVER paste inline
#   ./release.sh                      # builds + tests + uploads current version
#   ./release.sh --dry-run            # build + check only, no upload
#
# The token is read from $PYPI_TOKEN (env) only — it is never written to disk,
# git, or the command line.
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

# 1. version consistency across files
ver_py=$(grep -E '^version' pyproject.toml | head -1 | sed -E 's/.*"(.*)".*/\1/')
ver_init=$($PY -c "import re,io;print(re.search(r'\"(.*?)\"', open('bidreader/__init__.py').read().split('__version__')[1]).group(1))")
ver_cff=$(grep -E '^version:' CITATION.cff | sed -E 's/.*"(.*)".*/\1/')
echo "versions -> pyproject:$ver_py  __init__:$ver_init  CITATION:$ver_cff"
if [[ "$ver_py" != "$ver_init" || "$ver_py" != "$ver_cff" ]]; then
  echo "✗ version mismatch — align pyproject.toml / bidreader/__init__.py / CITATION.cff"; exit 1
fi
VER="$ver_py"

# 2. refuse to publish a version that already exists on PyPI
if [[ $DRY_RUN -eq 0 ]]; then
  live=$(curl -s "https://pypi.org/pypi/bidreader/$VER/json" -o /dev/null -w "%{http_code}")
  if [[ "$live" == "200" ]]; then
    echo "✗ bidreader $VER already on PyPI — bump the version first."; exit 1
  fi
fi

# 3. offline tests
echo "running tests..."
$PY -m pytest -q tests/

# 4. clean build + metadata check
echo "building $VER..."
rm -rf dist build ./*.egg-info
$PY -m build
$PY -m twine check dist/*

# 5. upload (token from env only)
if [[ $DRY_RUN -eq 1 ]]; then
  echo "✓ dry run complete — built & checked dist/ for $VER (not uploaded)"; exit 0
fi
: "${PYPI_TOKEN:?Set PYPI_TOKEN env var (project-scoped pypi-... token). Never paste it inline.}"
echo "uploading $VER to PyPI..."
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" $PY -m twine upload "dist/bidreader-$VER"*
echo "✓ published: https://pypi.org/project/bidreader/$VER/"
echo "  reminder: tag the release ->  git tag v$VER && git push --tags"
