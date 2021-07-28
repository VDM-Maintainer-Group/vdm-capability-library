#!/usr/bin/env python3

def jsonify(func):
    import json
    from functools import wraps

    @wraps(func)
    def _wrap(*args, **kwargs):
        args = [json.loads(x) for x in args]
        kwargs = {k:json.loads(v) for (k,v) in kwargs.items()}
        res = json.dumps( func(*args, **kwargs) )
        return res
    return _wrap
