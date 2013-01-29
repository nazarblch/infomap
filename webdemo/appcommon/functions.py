def map_dict(f, d):

    for k,v in d.items():
        d[k] = f(v)

    return d

