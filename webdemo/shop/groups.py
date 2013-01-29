# -*- coding: utf-8 -*-

import copy
from shop.groupModels import *

def make_group(l):
    groups=[]
    groups.append([l[0]])
    for i in l[1:]:
        if i.pattern not in [j[0].pattern for j in groups]: groups.append([i])
        else:
            for n in groups:
                if i.pattern==n[0].pattern: n.append(i)
    return groups

def check2pattern(pat1, pat2):
    if pat1==[]: return True
    else:
        j=0
        while pat1[0]!=pat2[j]:
            if j!=len(pat2)-1: j+=1
            else: break
        else:
            pat2.pop(j)
            return check2pattern(pat1[1:], pat2)

def minmax(gr1,gr2):
    if len(gr1[0].pattern)<len(gr2[0].pattern):
        m=gr1
        M=gr2
    else:
        M=gr1
        m=gr2
    return (m,M)


def accordance(gr1,gr2):
    acc=[]
    for i in gr1[0].pattern:
        acc.append([])
        for j, v in enumerate(gr2[0].pattern):
            if i==v: acc[-1].append(j)
    return acc


def row_in_word(group, num_word, position):
    return [i.as_word_class[num_word].word_as_list[position] for i in group]


def merge_or_not(gr1,gr2):
    (gr1, gr2)=minmax(gr1,gr2)
    if check2pattern(gr1[0].pattern,copy.deepcopy(gr2[0].pattern)):
        acc=accordance(gr1,gr2)


    else: return False


def find_parentgroups(gr, num, groups):
    candidatrs = []

    for ind,group in enumerate(groups):
        if ind != num and len(gr.pattern)<=len(group.pattern) and check2pattern(gr.pattern,copy.deepcopy(group.pattern)):
            candidatrs.append(ind)

    return candidatrs


'''
a=('str1 word1 word2',u'str1 word1 хрен авапав','word1 word2 str1 a', u'str1 word1 хрен')
'''
def compare(kws):
    num_words={}
    num_words_rev={}
    kw_num=[]
    i=1
    for kw in kws:
        for wd in kw.split():
            if wd in num_words: continue
            else:
                num_words[wd]=i
                num_words_rev[i]=wd
                i+=1
        kw_num.append([num_words[wd] for wd in kw.split()])

    lst_minus=[]
    for i, v in enumerate(kw_num):
        lst_minus.append([])
        tmp=[]
        for j in kw_num:
            total=(set(v) & set(j))
            if len(set(total))==len(set(v)) and list(set(j)-set(total)):
                tmp.extend(list(set(j)-set(total)))

        lst_minus[-1].extend([num_words_rev[i] for i in list(set(tmp))])
    return lst_minus


def find_nearest_groups(Mg, phr, border):
    maxscore = 0
    maxscoreind = None
    maxscorepatt = None
    wordsoutset = set()
    friq = int(phr[1])

    for k,gr in enumerate(Mg):
        score,patt,wordsout = gr.kwphrase_check(phr[0], friq)
        if len(wordsoutset)>0: wordsoutset &= set(wordsout)
        else: wordsoutset = set(wordsout)

        if score > max(maxscore, border):
            maxscore = score
            maxscoreind = k
            maxscorepatt = patt

    if maxscoreind != None:
        nearest_gr = Mg[maxscoreind]

        pattkey = str(sorted(maxscorepatt.values()))
        if nearest_gr.kwpatt.has_key(pattkey): nearest_gr.kwpatt[pattkey][1] += friq
        else: nearest_gr.kwpatt[pattkey] = [maxscorepatt, friq]

        '''
        for mod in nearest_gr.models:
            modkwphr = mod.get_subphrathe(maxscorepatt, nearest_gr.pattern)
            if len(modkwphr) > 0:
                if mod.kwphr.has_key(" ".join(modkwphr)): mod.kwphr[" ".join(modkwphr)] += friq
                else: mod.kwphr[" ".join(modkwphr)] = friq
        '''

        return maxscoreind, wordsoutset

    else:
        return None, wordsoutset


def join_groups(Mg):
    deleted = set()
    Mgcount = len(Mg)
    k = 0
    while k < Mgcount:
        gr = Mg[k]

        parents = find_parentgroups(gr, k, Mg)
        degarr = []
        selfdeg = gr.getW()
        maxdeg = 0.0
        maxdegpar = -1
        if len(parents)>0:
            for p in parents:
                parselfdeg = Mg[p].getW()
                positions,degin = Mg[p].subgroup_pos(Mg[k])
                degarr.append(degin)
                if degin > maxdeg and (parselfdeg <= degin or selfdeg <= degin) and p not in deleted :
                    maxdeg = degin
                    maxdegpar = p
                    maxdegpos = positions
            if maxdegpar != -1:
                Mg[maxdegpar].addsubgroup(gr, maxdegpos)
                deleted.add(k)
                del Mg[k]
                Mgcount -= 1
                continue

        print str(k)+" "+ str(maxdegpar) +" "+ str(maxdeg) +" "+str(zip(parents,degarr))

        k += 1

    return Mg


def makeMg_from_ajax(modelspost, modnumarr):

    modnumarr = modnumarr.split('&');
    modnumarr = filter(lambda s: len(s)>0, modnumarr)

    list_gr = []

    for modnum in modnumarr:
        modnum = modnum.strip().split(' ')
        modnum = map(lambda i: int(i), modnum)

        list_gr.append([model(mod[1], mod[0], '&') for mod in filter(lambda (k,v): str(k).isdigit() and int(k) in modnum, modelspost.iteritems() )])


    Mg = []
    for gr in list_gr:
        Mg_i = ModelGroup(gr)
        Mg_i.update_pattern()
        Mg.append(Mg_i)

    return Mg

def make_ven_cat_syn_phrs(VENDOR, CATEGORY, ven_syn, cat_syn):

    venarr = set([ven.name for ven in ven_syn])
    venarr.add(VENDOR)

    catarr = set([cat.name for cat in cat_syn])
    catarr.add(CATEGORY)

    res = [CATEGORY+" "+VENDOR]

    for  cat in catarr:
        for ven in venarr:
            if cat == CATEGORY and ven == VENDOR: continue
            res.append(cat+" "+ven)

    return res



def get_popul_gr_phrs(Mg,shift=0, prefixarr=[]):
    phr_gr_nums = {}

    for k,gr in enumerate(Mg):

        addphrs = gr.get_populest_subphrathes(shift)

        for phr in addphrs:
            if phr_gr_nums.has_key(phr): phr_gr_nums[phr].append(k)
            else: phr_gr_nums[phr] = [k]

    new_phr_gr_nums = {}
    for prefix in prefixarr:
        for phr,nums in phr_gr_nums.items():
            new_phr_gr_nums[prefix+" "+phr] = nums

    return new_phr_gr_nums





