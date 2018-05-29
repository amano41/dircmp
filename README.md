dircmp
======

Python script for comparing two directories.

## treecmp.py

Compare two directories recursively to check if they have the same directory structure.
The files are compared by their sizes and times.
With `-f` or `--full` option, you can compare the contents of the files.

## hashcmp.py

Compare the contents of two directories by comparing the hashes of all the files in them.
This script calculates the hashes of all the files in two directories and compares the hash of each files in the one directory with that of in the other directory.
