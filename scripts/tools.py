from itertools import islice
from collections import Counter

def take(it, n):
    return list(islice(it, n))

def hist(it):
    h = Counter()
    for i in it:
        h[i] += 1
    return h
