# -*-PYTHON-*-

from __future__ import print_function

def nav(d, ks):
    def nav2(d, ks):
        if len(ks) == 0:
            return d
        if not isinstance(d, dict):
            raise KeyError(ks)
        if ks[0] not in d:
            return None
        return nav2(d[ks[0]], ks[1:])
    return nav2(d, ks.split('.'))

if __name__ == "__main__":
    assert(nav({'a': {'b': {'c': 3}}}, 'a.b.c') == 3)
    try:
        x = nav({'a': {'b': {'c': 3}}}, 'a.b.c.d')
    except KeyError:
        pass
    assert(nav({'a': {'b': {'c': 3}}}, 'a.b') == {'c': 3})
    assert(nav({'a': {'b': ['c', 3]}}, 'a.b') == ['c', 3])

