# -*- coding: utf-8 -*-
import os
from transl import check_lang
from pymorphy import get_morph

try:
    import cdb
    from pymorphy.django_conf import default_morph as morph
except:
    morph = get_morph(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'morph'))

    
def all_declinations(str):    #        создание списка всех склонений строки
    
    cases = ['им', 'рд', 'дт','вн','тв','пр']
    number = ['ед', 'мн']
    case_num = [','.join([case, num]) for case in cases for num in number]
    
    finish =[]
    
    for cs in case_num:
        tmp =[]
        for word in str.split():
            if check_lang(word) == 'ru':
                tmp.append(morph.inflect_ru(unicode(word).upper(), unicode(cs, "utf-8")))
            else:
                tmp.append(word)
         
        finish.append(' '.join(tmp))
    
    finish = set(finish)
    finish = list(finish)
    
    finish = [str.lower() for str in finish]
    return finish



def find_im(lst):#        находит им.п
    lst = [unicode(str).upper() for str in lst]
    im =[]
    not_im =[]
    
    for j, str in enumerate(lst):
        iten = iter(range(len(str)))

        for i, word in enumerate(str.split()):
            if check_lang(word) != 'ru':
                ien = iten.next()
                if i < len(str.split()) - 1: continue
                elif ien == len(str) - 1:
                    not_im.append(str)
                    continue
                else:
                    im.append(str)
                    continue
                        
            if u'им' in reduce(lambda x,y: ' '.join([x,y]) ,[var['info'] for var in morph.get_graminfo(word)]):
                if i == len(str.split()) - 1:
                    im.append(str)
            else:
                not_im.append(str)
                break
    
    im = [word.lower() for word in im]
    not_im = [word.lower() for word in not_im]
        
    im_noim = {'im': im, 'not_im': not_im}
    return im_noim


def leave_mn(lst): #        Чистит список оставляя мн.ч если такое есть
    lst = [unicode(str).upper() for str in lst]
    lst_mn =[]
       
    for str in lst:
        lst_mn.append(' '.join(map(lambda word: morph.pluralize_ru(word) if check_lang(word) == 'ru' else word ,str.split())))
           
    mn = []
    for i in range(len(lst)):
        if lst_mn[i] in mn: continue
        it = iter(range(len(lst)))
        
        for j in range(len(lst)):
            
            if lst_mn[i] == lst_mn[j] and i != j:
                it.next()
                if lst[i] == lst_mn[i]: mn.append(lst[i])
                else: mn.append(lst[j])
                
            if j == len(lst) -1 and it.next() == 0:
                mn.append(lst[i])
                
    mn = [word.lower() for word in mn]
    
    return mn




