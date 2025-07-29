#!/bin/bash

rm -v enum/*.json
for f in json/components_*.json; do
    python3 enumerate.py "$f"
done
python3 enumerate.py json/connections.json
