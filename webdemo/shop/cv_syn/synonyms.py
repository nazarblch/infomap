# -*- coding: utf-8 -*-
import os
import difflib
import re
from itertools import ifilterfalse,permutations


from ya_func import suggestion, wordstat_search_also
from transl import translit, find_substr_in_arr, check_lang

from morph import all_declinations, find_im, leave_mn
from collections import deque
from oper import list_del_bad, del_str



class Vendor_synonyms:

    def __init__(self, vendor, method='sug', **kwargs):
        self.dbtable="ven"
        vendor=unicode(vendor).lower()
        self.vendor = vendor
        self.otherwords = [unicode(word, "utf-8") for word in ['купить', 'цена']]

        if 'add_ow' in kwargs:
            self.add_otherwords(kwargs['add_ow'])

        if method == 'sug':
            self.synonyms = self.synonyms_suggestions(vendor)
        if method == 'ws':
            self.synonyms = self.synonyms_wordstat(vendor)

    def add_otherwords(self, words):
        words = [unicode(word, "utf-8") for word in words]
        self.otherwords.extend(words)

    def synonyms_suggestions(self, vendor):
        vendor_suggestion = list(suggestion([vendor]))
        for_suggestion = set(vendor_suggestion[:5])
        for_suggestion.update(map(lambda word: ' '.join([vendor,word]),self.otherwords))
        for_suggestion = list(for_suggestion)

        yandex_trash = suggestion(for_suggestion)

        synonyms = self.check_synonyms(yandex_trash, vendor)

        if len(synonyms) == 0: synonyms = self.synonyms_wordstat(vendor)

        return synonyms


    def synonyms_wordstat(self, vendor):
        search_frases = [vendor]
        first_letters = set([])
        if check_lang(vendor) == 'en':
            if len(vendor.split()) > 1:
                fl  = [word[0] for word in vendor.split()]
                first_letters.add(''.join(fl))
                first_letters.add(' '.join(fl))
        yandex_trash = wordstat_search_also([vendor])[0]

        synonyms = self.check_synonyms(yandex_trash, vendor)

        if len(first_letters) > 0:
            yandex_words = set(reduce(lambda phr1, phr2: ' '.join([phr1,phr2]), yandex_trash).split())
            intersection = yandex_words & first_letters
            if  intersection != 0: synonyms.update(intersection)
        return synonyms

    def add_wordstat(self, vendor=""):
        if vendor == "": vendor = self.vendor
        new = self.synonyms_wordstat(vendor) - set(self.synonyms)
        return set(new)


    def check_synonyms(self, synonyms_start, vendor):
        synonyms_finish = set(find_substr_in_arr(vendor, synonyms_start, cutoff=0.7, variants=1))
        if check_lang(vendor) == 'en':
            synonyms_finish.update(find_substr_in_arr(translit(vendor), synonyms_start, cutoff=0.7, variants=1))

        synonyms_finish.difference_update([vendor])
        return synonyms_finish



PHR_NUM = 10
class Category_synonyms:

    def __init__(self, category):
        self.dbtable="cat"
        self.bad_words = [unicode(word, "utf-8") for word in ['цена','дешевые', 'каталог','цены', 'продажа', 'куплю', 'купить', 'недорого', 'дешево', 'интернет магазин','бесплатно','продать', 'магазин']]
        self.otherwords = [unicode(word, "utf-8") for word in ['купить', 'цена', 'лучшие']]
        #self.synonyms = self.syn_suggestion(category, self.bad_words)
        self.category_suggestion = []
        self.cur_depth = 1
        self.cur_phr_q = deque([category])
        self.cur_phr_q.extend([' '.join([category, word]) for word in self.otherwords])
        self.phr_div10 = []
        self.phr_mod10 = []
        self.obtained_phr = set([category])
        self.unchecked_words = set()


    def phrase_suggestion(self, phrase):
        suggest = suggestion([phrase])
        suggest_set = set(suggest)

        #suggest_set.update([' '.join([phrase, word]) for word in self.otherwords])

        return list(suggest_set)

    def clear_suggest(self, suggest_arr): #  checked_phr - all phrases currently checked by user
        '''
        bad_words also have to be 'scloned'
        '''
        suggest_arr = list_del_bad(suggest_arr, self.bad_words + list(self.unchecked_words))
        suggest_arr = set(suggest_arr) | self.obtained_phr

        suggest_arr = list(suggest_arr)

        im = find_im(suggest_arr)['im']
        not_im = find_im(suggest_arr)['not_im']

        im = list(set(im) - self.permutations_strings(im,'yes'))

        for_sclon = leave_mn(im)
        sclon = set([])
        for phr in for_sclon:
            sclon.update(all_declinations(phr))


        not_im = set(not_im)
        for_sclon = set(for_sclon)

        result = for_sclon | (not_im - sclon)

        result.difference_update(self.permutations_strings(self.obtained_phr))

        sclon = set([])
        for phr in self.obtained_phr:
            sclon.update(all_declinations(phr))

        result.difference_update(sclon)


        return list(result)

    def permutations_strings(self, strings, remove = 'no'):
        per = set([])
        for str in strings:
            per.update(map(lambda x: ' '.join(x),permutations(str.split()) ))
            if remove == 'yes': per.remove(str)
        return per


    def phrase_suggestion_recursive(self, num_ya_req, new_unchecked_words, checked_phr=[]):

        self.unchecked_words |= set(new_unchecked_words)

        req_count = 0

        self.phr_div10 = self.phr_mod10[:PHR_NUM]
        if len(self.phr_mod10) >= PHR_NUM:
            self.phr_mod10 = self.phr_mod10[PHR_NUM:]
        else:
            self.phr_mod10 = []

        while len(self.cur_phr_q) > 0 and len(self.phr_div10) < PHR_NUM and req_count < num_ya_req:
            phrase = self.cur_phr_q.popleft()
            suggest_arr = self.phrase_suggestion(phrase)

            self.obtained_phr |= set(checked_phr)

            suggest_arr = list(set(suggest_arr) - self.obtained_phr)

            suggest_arr = self.clear_suggest(suggest_arr)

            req_count += 1

            self.cur_phr_q.extend(suggest_arr)
            self.obtained_phr |= set(suggest_arr)
            self.phr_div10 += suggest_arr

            if len(self.phr_div10) > PHR_NUM:
                self.phr_mod10 += self.phr_div10[PHR_NUM:]
                self.phr_div10 = self.phr_div10[:PHR_NUM]


























