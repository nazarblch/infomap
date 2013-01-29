# -*- coding: utf-8 -*-
from synonyms import *
from file_rw import *
from ya_func import suggestion


before_suggestion=r_lst_of_str('in.txt')

category = before_suggestion[0]

print category

f = open('out.txt', 'w')
'''

ob=Category_synonyms(category)

for i in range(2):

    ob.phrase_suggestion_recursive( 10, [])

    for syn in ob.phr_div10:
        print syn

    print "-----"
    print len(ob.cur_phr_q)
    print "-----"


for i in range(2):

    ob.phrase_suggestion_recursive( 10, ['купить','3d'])

    for syn in ob.phr_div10:
        print syn

    print "-----"
    print len(ob.cur_phr_q)
    print "-----"



print "++++++++++++"

for syn in ob.obtained_phr:
    print syn



'''
ob=Vendor_synonyms(category, method='sug')

for syn in ob.synonyms:
    print syn

