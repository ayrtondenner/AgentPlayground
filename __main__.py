"""Root entrypoint shim.

Recommended usage:

    python -m agent_playground

This file stays so running `python __main__.py` still works.
"""

from agent_playground.__main__ import main


if __name__ == "__main__":
    main()