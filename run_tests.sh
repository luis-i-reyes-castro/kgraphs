#!/bin/bash

rm -v enum/*.json
python3 enumerate.py json/test1.json
python3 enumerate.py json/test2.json
