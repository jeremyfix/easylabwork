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

if __name__ == '__main__':
    res = myfunction(1)
    print(f"The result of the function call is {res}")
