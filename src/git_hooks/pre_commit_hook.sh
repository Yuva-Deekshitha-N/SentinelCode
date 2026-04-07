#!/bin/sh
cd "$(git rev-parse --show-toplevel)"
python -m src.git_hooks.pre_commit
