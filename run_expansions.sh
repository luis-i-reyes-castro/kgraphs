#!/bin/bash

# Target directory
DIR_FETCH_CMD="import constants; print(constants.DIR_DKNOWLEDGE_B)"
DIR_NAME=$(python3 -c "$DIR_FETCH_CMD")
# Check if directory exists, create if it doesn't
if [ ! -d "$DIR_NAME" ]; then
    echo "Creating directory: $DIR_NAME"
    mkdir -p "$DIR_NAME"
else
    rm -v "$DIR_NAME"/*.json
fi

python3 placeholder_expansion.py
python3 compute_paths.py
