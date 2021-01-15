#!/usr/bin/env python3
# coding: utf-8

# Standard imports
import os
import sys
from typing import Union
import pathlib
from pathlib import Path

_TEMPLATE_TAG = "#@TEMPL@"
_SOLUTION_TAG = "@SOL@"
_SOLUTION_BLOCK_START = "#@SOL"
_SOLUTION_BLOCK_END = "#SOL@"


class IdxSelector(object):

    def __init__(self, max_lines, slices, keep):
        self.keep = keep
        self.max_lines = max_lines
        self.slices = slices
        self.slice_iterator = slices
        self.idx = 0
        self.current_slice = self.get_next_slice()

    def get_next_slice(self):
        try:
            return next(self.slice_iterator)
        except StopIteration:
            return None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):

        def is_in_slice(idx, cur_slice):
            return cur_slice is not None and cur_slice[0] <= idx <= cur_slice[1]
        
        if self.idx < self.max_lines:
            print(f"{self.idx} / {self.max_lines}")
            # We test if the index is in the current slice
            if is_in_slice(self.idx, self.current_slice):
                value = self.keep
            else:
                value = not self.keep
            if self.current_slice is not None and self.idx > self.current_slice[1]:
                self.current_slice = self.get_next_slice()
            self.idx += 1
            return value
        print("Stopping")
        raise StopIteration()


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
    output_lines = list(map(remove_template, output_lines))

    # Remove the SOL blocks
    for i, li in enumerate(output_lines):
        start_blocks_idx = [i for i, li in enumerate(output_lines) if li.find(_SOLUTION_BLOCK_START) != -1]
        end_blocks_idx = [i for i, li in enumerate(output_lines) if li.find(_SOLUTION_BLOCK_END) != -1]

    if len(start_blocks_idx) != len(end_blocks_idx):
        raise RuntimeError("Non matching opening or ending solution blocks."
                           " Did all your #@SOL has their corresponding"
                           " #SOL@ and vice versa ?")

    line_selector = IdxSelector(len(output_lines),
                                zip(start_blocks_idx, end_blocks_idx),
                                keep=False)
    output_lines = [li for li, keepi in zip(output_lines, line_selector) if keepi]

    return "".join(output_lines)


def process_file(filepath: Union[Path, str],
                 targetpath: Union[Path, str]):
    '''
    Process a single file
    '''
    print(filepath)
    with open(filepath, 'r') as fh:
        reslines = clean_file(fh)
    with open(targetpath, 'w') as fh:
        fh.write(reslines)


def process_directory(sourcepath: Union[Path, str],
                      targetpath: Union[Path, str]):

    if isinstance(sourcepath, str):
        sourcepath = Path(sourcepath)

    if isinstance(targetpath, str):
        targetpath = Path(targetpath)

    # The source directory must exist
    assert(sourcepath.is_dir())

    # The target directory must not exist
    assert(not targetpath.is_dir())
    targetpath.mkdir()

    for path in sourcepath.glob('**/*'):
        src_filepath = path
        tgt_filepath = targetpath / path.relative_to(sourcepath)
        if src_filepath.is_dir():
            tgt_filepath.mkdir()
        else:
            process_file(src_filepath, tgt_filepath)


def main():
    if len(sys.argv) != 3:
        print(f"Usage : {sys.argv[0]} source_dir target_dir")
        sys.exit(-1)

    process_directory(sys.argv[1],
                      sys.argv[2])
