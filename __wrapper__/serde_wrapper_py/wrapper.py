#!/usr/bin/env python3

def jsonify(func):
    import json
    from functools import wraps

    @wraps(func)
    def _wrap(kwargs):
        for (k,v) in kwargs.items():
            kwargs[k] = json.loads(v)
        res = json.dumps( func(**kwargs) )
        return res
    return _wrap
