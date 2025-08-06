#!/bin/bash

rm expansions/*.json
python3 parsing.py
python3 compute_paths.py
