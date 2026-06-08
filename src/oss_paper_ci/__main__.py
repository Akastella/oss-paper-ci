"""Allow running as `python -m oss_paper_ci`."""

import sys
from oss_paper_ci.cli import main

if __name__ == "__main__":
    sys.exit(main())
