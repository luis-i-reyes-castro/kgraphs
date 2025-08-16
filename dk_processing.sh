#!/bin/bash

# Load target directory name
DIR_PRINT_CMD="import abc_project_vars; print(abc_project_vars.DIR_DKB)"
DIR_NAME=$(python3 -c "$DIR_PRINT_CMD")
# If directory exists then remove all its contents
if [ -d "$DIR_NAME" ]; then
    rm -v "$DIR_NAME"/*.json
    rm -v "$DIR_NAME"/*.md
fi

# Run expansions and compute paths
python3 dka_parse_placeholders.py
python3 dkb_compute_paths.py
# python3 dkb_publish_errors_list.py
