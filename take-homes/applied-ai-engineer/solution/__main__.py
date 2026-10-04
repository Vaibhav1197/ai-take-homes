"""Enables `py -m solution review` / `py -m solution apply` from the
applied-ai-engineer/ directory."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
