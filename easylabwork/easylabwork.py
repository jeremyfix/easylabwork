#!/usr/bin/env python3
# coding: utf-8

# Standard imports
import os
import sys
from typing import Union
from pathlib import Path

_TEMPLATE_TAG = "#@TEMPL@"
_SOLUTION_TAG = "@SOL@"

def clean_file(fh):
    ''' Process a single file by:
        1- removing the lines ending by the _SOLUTION_TAG
        2- removing any occurences of _TEMPLATE_TAG

        Returns a cleaned string
    '''
    lines = fh.readlines()

    # Remove the lines containing _SOLUTION_TAG
    output_lines = [l for l in lines if l.find(_SOLUTION_TAG) == -1]

    # Remove the tags _TEMPLATE_TAG
    def remove_template(line):
        idx = line.find(_TEMPLATE_TAG)
        if idx != -1:
            return line[:idx] + line[(idx+len(_TEMPLATE_TAG)):]
        else:
            return line
    output_lines = map(remove_template, output_lines)

    return "".join(output_lines)


def process_file(filepath: Union[Path, str],
                 targetpath: Union[Path, str]):
    '''
    Process a single file

    '''
    with open(filepath, 'r') as fh:
        reslines = clean_file(fh)
    with open(targetpath, 'w') as fh:
        fh.write(reslines)


def main():
    if len(sys.argv) != 2:
        print(f"Usage : {sys.argv[0]} source_dir target_dir")
    process_file(sys.argv[1], "target.py")
