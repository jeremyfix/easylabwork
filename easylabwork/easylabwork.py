#!/usr/bin/env python3
# coding: utf-8

# Standard imports
import sys
from typing import Union
from pathlib import Path
import shutil

_TEMPLATE_TAG = "# @TEMPL@"
_TEMPLATE_BLOCK_START = "@TEMPL"
_TEMPLATE_BLOCK_END = "TEMPL@"
_SOLUTION_TAG = "@SOL@"
_SOLUTION_BLOCK_START = "@SOL"
_SOLUTION_BLOCK_END = "SOL@"


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
                    "Warning: You have two consecutive blocks without even"
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

        def is_start_slice(idx, cur_slice):
            return cur_slice is not None and cur_slice[0] == idx

        def is_end_slice(idx, cur_slice):
            return cur_slice is not None and cur_slice[1] == idx

        if self.idx < self.max_lines:
            # We test if the index is in the current slice
            is_start = is_start_slice(self.idx, self.current_slice)
            is_end = is_end_slice(self.idx, self.current_slice)
            is_in = is_in_slice(self.idx, self.current_slice)
            if self.current_slice is not None and self.idx > self.current_slice[1]:
                self.to_next_slice()
            self.idx += 1
            return is_start, is_in, is_end
        raise StopIteration()


def clean_file(fh):
    """Process a single file by:
    1- Removing the lines ending by the _SOLUTION_TAG
    2- Removing any occurences of _TEMPLATE_TAG

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
    start_blocks_idx = [
        i for i, li in enumerate(output_lines) if li.find(_SOLUTION_BLOCK_START) != -1
    ]
    end_blocks_idx = [
        i for i, li in enumerate(output_lines) if li.find(_SOLUTION_BLOCK_END) != -1
    ]

    if len(start_blocks_idx) != len(end_blocks_idx):
        starting_lines_msg = f"Found '{_SOLUTION_BLOCK_START}' on lines {[l+1 for l in start_blocks_idx]}"
        ending_lines_msg = (
            f"Found '{_SOLUTION_BLOCK_END}' on lines {[l+1 for l in end_blocks_idx]}"
        )
        raise RuntimeError(
            "Non matching opening or ending solution blocks."
            f" Did all your {_SOLUTION_BLOCK_START} has their corresponding"
            f" {_SOLUTION_BLOCK_END} and vice versa ?"
            + "\n"
            + starting_lines_msg
            + "\n"
            + ending_lines_msg
        )

    line_selector = IdxSelector(
        len(output_lines), zip(start_blocks_idx, end_blocks_idx)
    )
    output_lines = [
        li for li, (_, is_in, _) in zip(output_lines, line_selector) if not is_in
    ]

    # Process the TEMPL blocks
    # the opening and closing should be removed
    # the lines in between must be uncommented
    start_blocks_idx = [
        i for i, li in enumerate(output_lines) if li.find(_TEMPLATE_BLOCK_START) != -1
    ]
    end_blocks_idx = [
        i for i, li in enumerate(output_lines) if li.find(_TEMPLATE_BLOCK_END) != -1
    ]

    if len(start_blocks_idx) != len(end_blocks_idx):
        starting_lines_msg = f"Found '{_TEMPLATE_BLOCK_START}' on lines {[l+1 for l in start_blocks_idx]}"
        ending_lines_msg = (
            f"Found '{_TEMPLATE_BLOCK_END}' on lines {[l+1 for l in end_blocks_idx]}"
        )
        raise RuntimeError(
            "Non matching opening or ending template blocks."
            f" Did all your {_TEMPLATE_BLOCK_START} has their corresponding"
            f" {_TEMPLATE_BLOCK_END} and vice versa ?"
            + "\n"
            + starting_lines_msg
            + "\n"
            + ending_lines_msg
        )

    line_selector = IdxSelector(
        len(output_lines), zip(start_blocks_idx, end_blocks_idx)
    )
    lines = []
    for li, (is_start, is_in, is_end) in zip(output_lines, line_selector):
        next_line = li
        if is_start or is_end:
            # discard the line
            continue
        else:
            if is_in:
                # If this is neither the opening or closing
                #
                # rm the leading '# '
                first_comment_idx = next_line.find("# ")
                li = li[:first_comment_idx] + li[first_comment_idx + 2 :]
            lines.append(li)
    return "".join(lines)


def process_file(filepath: Union[Path, str], targetpath: Union[Path, str]):
    """
    Process a single file
    """
    try:
        print(f"Processing {filepath}")
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
