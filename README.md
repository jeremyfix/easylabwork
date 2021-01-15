# Easylabwork

It can be tricky (or at least cumbersome) to prepare labworks when you want to provide starter code to your students still ensuring that the code will be running correctly if you inject your solution in this template code.

You may be tempted to code in parallel both the starter code and the solution but updating both is cumbersome. You may be tempted to write your solution to ensure the code is ok but then it is time consuming to remove your solution code to prepare the starter code and then, for updating, you fall back to the first situation.

The way proposed by easylabwork is to prepare a merged version of starter code and solution code and then to apply the easylabwork script on it to split it into the starter code and the solution code. You must equip your code with special tags indicating to easylabwork which lines need to be removed.

## How to install

To install, use pip :

```bash
python3 -m pip install git+https://github.com/jeremyfix/easylabwork.git
```

It is not yet on Pypi.

## Processing a single file

For now on, easylabwork is though for python programming and renders a tagged code :

```python

def myfunction(value: float):
    '''
    Args:
        value: the value on which to apply the function

    Returns:
        res (float): the result of this operation
    '''

    # Square the value
    #@TEMPL@sq_value = None
    sq_value = value**2  #@SOL@

    return sq_value
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
```


