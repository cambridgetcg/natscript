#!/bin/bash
# natscript — install in 10 seconds
# Requires: Python 3.8+
set -e

if command -v pip3 >/dev/null 2>&1; then
  pip3 install https://github.com/cambridgetcg/natscript/releases/download/v0.1.0/natscript-0.1.0-py3-none-any.whl --user
  echo "✓ natscript installed. Run: python3 -m natscript -e 'say \"hello\"'"
elif command -v pip >/dev/null 2>&1; then
  pip install https://github.com/cambridgetcg/natscript/releases/download/v0.1.0/natscript-0.1.0-py3-none-any.whl --user
  echo "✓ natscript installed. Run: python3 -m natscript -e 'say \"hello\"'"
else
  echo "✗ need pip. Install Python 3.8+ first."
  exit 1
fi
