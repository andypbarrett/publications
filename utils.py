def _traverse_dict(obj, list_of_keys):
    if not isinstance(obj, dict):
        return obj
    else:
        return _traverse_dict(obj.get(list_of_keys.pop(0)), list_of_keys)

def _find_value(list_of_objs, list_of_keys, depth=2, default=None):
    """Returns a value along a given path in a json-type structure"""
    for obj in list_of_objs[:depth]:
        value = _traverse_dict(obj, list_of_keys)
        if value:
            return value
    return default
    
