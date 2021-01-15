#!/usr/bin/env python3
# coding: utf-8

# Standard imports
import sys


def syr(stem: int):
    '''
    Compute the serie of Syracuse up to the limit cycle
    '''

    value = stem

    while(value != 1):
        #@TEMPL
        #if None:
        #    value = None
        #else:
        #    value = None
        #TEMPL@
        #@SOL
        if value % 2 == 0:
            value = value // 2
        else:
            value = 3 * value + 1
        #SOL@
        sys.stdout.write(f"{value} ")
        sys.stdout.flush()
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} value")
        sys.exit(-1)

    syr(int(sys.argv[1]))
