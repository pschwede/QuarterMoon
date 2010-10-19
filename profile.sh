#!/bin/bash

cd src/
python -m cProfile -scumulative Controller.py > ../profile.txt
