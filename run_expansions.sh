#!/bin/bash

# Target directory
DATA_DIR="data_expanded/"
# Check if directory exists, create if it doesn't
if [ ! -d "$DATA_DIR" ]; then
    echo "Creating directory: $DATA_DIR"
    mkdir -p "$DATA_DIR"
else
    rm "$DATA_DIR"*.json
fi

python3 parse_placeholders.py
python3 compute_paths.py
