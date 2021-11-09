#!/usr/bin/env python3

def jsonify(func):
    import json
    from functools import wraps

    @wraps(func)
    def _wrap(kwargs):
        kwargs = json.loads(kwargs)
        res = json.dumps( func(**kwargs) )
        return res
    return _wrap
