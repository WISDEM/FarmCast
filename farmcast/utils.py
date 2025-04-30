def getMultipleOf(val, multipleof):
    '''
    Get integer multiple of a quantity.
        The val/multipleof quantity can be within numerical error of an integer
        and so additional care must be take
    '''
    valmult = int(round(val/multipleof,6))*multipleof
    return round(valmult, 4)