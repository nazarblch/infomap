# -*- coding: utf-8 -*-
import os
from transl import translit, check_lang
from itertools import  permutations
from pymorphy import get_morph
morph = get_morph(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'morph'))

def permutations_strings(strings, remove = 'no'):
    per = set([])
    for str in strings:
        per.update(map(lambda x: ' '.join(x),permutations(str.split()) ))
        if remove == 'yes': per.remove(str)
    return list(per)

lst = ['abc asd','def dfg' ,'try']

print permutations_strings(lst, 'yes')
