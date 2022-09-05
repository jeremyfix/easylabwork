# Easylabwork

It can be tricky (or at least cumbersome) to prepare labworks when you want to provide starter code to your students still ensuring that the code will be running correctly if you inject your solution in this template code.

You may be tempted to code in parallel both the starter code and the solution but updating both is cumbersome. You may be tempted to write your solution to ensure the code is ok but then it is time consuming to remove your solution code to prepare the starter code and then, for updating, you fall back to the first situation.

The way proposed by easylabwork is to prepare a merged version of starter code and solution code and then to apply the easylabwork script on it to split it into the starter code and the solution code. You must equip your code with special tags indicating to easylabwork which lines need to be removed. The initial version is the solution code and can be executed for testing everything is running as expected.

## How to install

To install, use pip :

```bash
python3 -m pip install git+https://github.com/jeremyfix/easylabwork.git
```

It is not yet on Pypi.

## Usage

The package installs a program that parse files in a directory and make a mirror of this hierarchy with processed files. 

```bash
easylabwork examples examples_done
```

The above command will iterate in the examples directory and every processed file will be copied in the directory examples_done with a mirrored.

## Examples

### One line tags

For now on, easylabwork is thought for python programming and renders a tagged code :

```python

def myfunction(value: float):
    '''
    Args:
        value: the value on which to apply the function

    Returns:
        res (float): the result of this operation
    '''

    # Square the value
    # @TEMPL@ sq_value = None
    sq_value = value**2  # @SOL@

    return sq_value

if __name__ == '__main__':
    res = myfunction(1)
    print(f"The result of the function call is {res}")
```

into the starter code

```python

def myfunction(value: float):
    '''
    Args:
        value: the value on which to apply the function

    Returns:
        res (float): the result of this operation
    '''

    # Square the value
    sq_value = None

    return sq_value

if __name__ == '__main__':
    res = myfunction(1)
    print(f"The result of the function call is {res}")
```

### Block tags

We can tag blocks of code as below :

```python

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
        # @TEMPL
        # if None:
        #     value = None
        # else:
        #     value = None
        # TEMPL@
        # @SOL
        if value % 2 == 0:
            value = value // 2
        else:
            value = 3 * value + 1
        # SOL@
        sys.stdout.write(f"{value} ")
        sys.stdout.flush()
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} value")
        sys.exit(-1)

    syr(int(sys.argv[1]))
```

which is rendered as:

```python

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
        if None:
            value = None
        else:
            value = None
        sys.stdout.write(f"{value} ")
        sys.stdout.flush()
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} value")
        sys.exit(-1)
```
