#!/bin/bash

rm expansions/*.json
python3 parse_placeholders.py
python3 compute_paths.py
