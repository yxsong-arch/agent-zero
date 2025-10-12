#!/usr/bin/env python3
"""
Reload the Agent Zero knowledge index (vector DB) without restarting the app.

Usage (from repo root):
  python scripts/reload_knowledge.py
or
  py -3 scripts/reload_knowledge.py

This script adjusts sys.path to the repo root so it can import initialize.py
and the memory helper, then triggers a reload.
"""
import sys
import os
import asyncio


def repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))


async def _reload():
    # Ensure we can import project modules
    root = repo_root()
    if root not in sys.path:
        sys.path.insert(0, root)
    os.chdir(root)

    from python.helpers import memory  # type: ignore
    import initialize  # type: ignore

    agent = initialize.initialize_agent()
    await memory.Memory.reload(agent)
    print("Knowledge reloaded")


def main() -> int:
    try:
        asyncio.run(_reload())
        return 0
    except Exception as e:
        # Print a concise error for quick diagnosis
        sys.stderr.write(f"Knowledge reload failed: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
