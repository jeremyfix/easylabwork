#!/usr/bin/env python3
# coding: utf-8

# Standard imports
import sys
from typing import Union
from pathlib import Path
import shutil

_TEMPLATE_TAG = "# @TEMPL@ "
_TEMPLATE_BLOCK_START = "# @TEMPL"
_TEMPLATE_BLOCK_END = "# TEMPL@"
_SOLUTION_TAG = "@SOL@"
_SOLUTION_BLOCK_START = "# @SOL"
_SOLUTION_BLOCK_END = "# SOL@"


class IdxSelector(object):
    def __init__(self, max_lines, slices):
        self.max_lines = max_lines
        self.slices = slices
        self.slice_iterator = slices
        self.idx = 0
        self.current_slice = None
        self.to_next_slice()

    def to_next_slice(self):
        try:
            prev_slice = self.current_slice
            self.current_slice = next(self.slice_iterator)
            if self.current_slice[1] < self.current_slice[0]:
                raise RuntimeError(
                    f"Mismatch between the closing block at"
                    f" line {self.current_slice[1]+1} and opening"
                    f" block at line {self.current_slice[0]+1}"
                )
            if (
                prev_slice is not None
                and self.current_slice is not None
                and prev_slice[1] + 1 == self.current_slice[0]
            ):
                print(
                    f"Warning: You have two consecutive blocks without even"
                    " a line in between, there will remain a comment"
                    " in the result"
                )
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
            # We test if the index is in the current slice
            is_in = is_in_slice(self.idx, self.current_slice)
            if self.current_slice is not None and self.idx > self.current_slice[1]:
                self.to_next_slice()
            self.idx += 1
            return is_in
        raise StopIteration()


def clean_file(fh):
    """Process a single file by:
    1- removing the lines ending by the _SOLUTION_TAG
    2- removing any occurences of _TEMPLATE_TAG

    Returns a cleaned string
    """
    lines = fh.readlines()

    # Remove the lines containing _SOLUTION_TAG
    output_lines = [l for l in lines if l.find(_SOLUTION_TAG) == -1]

    # Remove the tags _TEMPLATE_TAG
    def remove_template(line):
        idx = line.find(_TEMPLATE_TAG)
        if idx != -1:
            return line[:idx] + line[(idx + len(_TEMPLATE_TAG)) :]
        else:
            return line

    output_lines = list(map(remove_template, output_lines))

    # Remove the SOL blocks
    for i, li in enumerate(output_lines):
        start_blocks_idx = [
            i
            for i, li in enumerate(output_lines)
            if li.find(_SOLUTION_BLOCK_START) != -1
        ]
        end_blocks_idx = [
            i for i, li in enumerate(output_lines) if li.find(_SOLUTION_BLOCK_END) != -1
        ]

    if len(start_blocks_idx) != len(end_blocks_idx):
        raise RuntimeError(
            "Non matching opening or ending solution blocks."
            f" Did all your {_SOLUTION_BLOCK_START} has their corresponding"
            f" {_SOLUTION_BLOCK_END} and vice versa ?"
        )

    line_selector = IdxSelector(
        len(output_lines), zip(start_blocks_idx, end_blocks_idx)
    )
    output_lines = [li for li, is_in in zip(output_lines, line_selector) if not is_in]

    # Process the TEMPL blocks
    # The opening and closing should be removed
    # The lines in between must be uncommented
    for i, li in enumerate(output_lines):
        start_blocks_idx = [
            i
            for i, li in enumerate(output_lines)
            if li.find(_TEMPLATE_BLOCK_START) != -1
        ]
        end_blocks_idx = [
            i for i, li in enumerate(output_lines) if li.find(_TEMPLATE_BLOCK_END) != -1
        ]

    if len(start_blocks_idx) != len(end_blocks_idx):
        raise RuntimeError(
            "Non matching opening or ending solution blocks."
            f" Did all your {_TEMPLATE_BLOCK_START} has their corresponding"
            f" {_TEMPLATE_BLOCK_END} and vice versa ?"
        )

    line_selector = IdxSelector(
        len(output_lines), zip(start_blocks_idx, end_blocks_idx)
    )
    lines = []
    prev_line = None
    next_line = None
    was_in = False
    for li, is_in in zip(output_lines, line_selector):
        next_line = li
        if is_in:
            # We are in a block, we remove the first comment
            first_comment_idx = next_line.find("#")
            next_line = (
                next_line[:first_comment_idx] + next_line[first_comment_idx + 1 :]
            )
            if not was_in:
                # If we enter the block we do not keep the line
                next_line = None
        else:
            # We are not (maybe just leaving) a template block
            if was_in:
                # if we are just leaving the block, the last # TEMPL@
                # must be discarded
                prev_line = None
        if prev_line is not None and not was_in:
            lines.append(prev_line)
        prev_line = next_line
        was_in = is_in
    if prev_line is not None:
        lines.append(prev_line)

    return "".join(lines)


def process_file(filepath: Union[Path, str], targetpath: Union[Path, str]):
    """
    Process a single file
    """
    try:
        with open(filepath, "r") as fh:
            reslines = clean_file(fh)
        with open(targetpath, "w") as fh:
            fh.write(reslines)
        print(f"Processed {filepath} -> {targetpath}")
    except UnicodeDecodeError:
        # In this case, we just copy the file
        shutil.copy(filepath, targetpath)
        print(f"Copy {filepath} -> {targetpath}")


def process_directory(sourcepath: Union[Path, str], targetpath: Union[Path, str]):

    if isinstance(sourcepath, str):
        sourcepath = Path(sourcepath)

    if isinstance(targetpath, str):
        targetpath = Path(targetpath)

    # The source directory must exist
    assert sourcepath.is_dir()

    # The target directory must not exist
    assert not targetpath.is_dir()
    targetpath.mkdir()

    for path in sourcepath.glob("**/*"):
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

    if not Path(sys.argv[1]).is_dir():
        process_file(sys.argv[1], sys.argv[2])
    else:
        process_directory(sys.argv[1], sys.argv[2])
