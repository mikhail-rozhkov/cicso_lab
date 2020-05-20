#!/bin/bash

#Build => Test => Coverage
pip install coverage
coverage run ad-mysql.py test
coverage report -m
coverage html
echo "Open htmlcov/index.html"