# -*- coding: utf-8 -*-
from suds import WebFault
from shop.groups import make_group, ModelGroup, join_groups,make_ven_cat_syn_phrs, find_nearest_groups, get_popul_gr_phrs
from shop.groupModels import model
from yafunc import wordstat, budget_forecast



#Create array ModelGroup for fix vendor and category
#templ_dict - info about session
def Mg_for_vendor_category(shop, category, vendor):

    products = shop.products_set.filter(category=category, vendor=vendor)
    list_models=[model(prod.model, prod.id) for prod in products]
    list_gr=make_group(list_models)

    Mg = [ModelGroup(gr) for gr in list_gr]

    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)

    return Mg


def clear_unpopular_group_patterns(Mg):

    phr_for_forecast = {}

    patts_num_to_check = 0
    for grNum, gr in enumerate(Mg):
        if patts_num_to_check > 80: break

        for pattKey in gr.unchecked_patts:
            phr = " ".join(gr.models[0].get_subphrathe(gr.kwpatt[pattKey][0], gr.pattern))

            patts_num_to_check += 1

            if not phr_for_forecast.has_key(phr):
                phr_for_forecast[phr] = [(grNum, pattKey)]
            else:
                phr_for_forecast[phr].append((grNum, pattKey))

        gr.unchecked_patts = set()

    if phr_for_forecast.__len__() == 0: return

    forecast_dict = budget_forecast(phr_for_forecast.keys()[:100])

    for phr, data in forecast_dict.items():

        shows = int(data["Shows"])
        if shows < 100:

            grNum_pattKey_arr = phr_for_forecast[phr]

            for grNum, pattKey in grNum_pattKey_arr:
                del Mg[grNum].kwpatt[pattKey]



def wordstat_first_request(Mg, shopobj, category, vendor):
    ven_syn = shopobj.vendor_syns.filter(vendor=vendor)
    cat_syn = shopobj.category_syns.filter(category=category)
    req_phrs = make_ven_cat_syn_phrs(vendor.name, category.name, ven_syn, cat_syn)

    try:
        firstphrases = wordstat(req_phrs[:10], showsmax=20000, geos = [1,2])[0]
    except WebFault, e:
        print e
        firstphrases = wordstat(req_phrs[:10], showsmax=20000, geos = [1,2])[0]

    additional_wd = set()

    Mg = filter(lambda gr: len(gr.models)>0 , Mg)

    for phrasesarr in firstphrases:
        for phr in phrasesarr:
            num,wordsoutset = find_nearest_groups(Mg, phr, 0.2)
            for addwd in wordsoutset:
                additional_wd.add(addwd)

    #clear_unpopular_group_patterns(Mg)

    Mg_AddWd = {"Mg": Mg, "additional_wd": additional_wd}

    return Mg_AddWd

def wordstat_next_request( vendor, shift, Mg, border=0.19):

    if vendor is None:
        return None

    VENDOR = vendor.name


    phr_gr_nums = get_popul_gr_phrs(Mg, shift, [VENDOR])

    if len(phr_gr_nums) == 0:
        return -1

    req_phrs = phr_gr_nums.keys()

    try:
        kwphrases, req_phrases = wordstat(req_phrs[:50], showsmax=10000, geos = [1,2])
    except WebFault, e:
        print e
        kwphrases, req_phrases = wordstat(req_phrs[:50], showsmax=10000, geos = [1,2])

    additional_wd = {}

    bad_nums = set()

    for phrnum, req_phr in enumerate(req_phrases):

        for grnum in phr_gr_nums[req_phr]:
            if grnum in bad_nums: continue

            gr = Mg[grnum]

            if len(gr.models) == 0:
                Mg.pop(grnum)
                bad_nums.add(grnum)
                continue


            for phr in kwphrases[phrnum]:
                friq = int(phr[1])

                score,patt,wordsout = gr.kwphrase_check(phr[0], friq)

                if additional_wd.has_key(grnum): additional_wd[grnum] |= (wordsout)
                else: additional_wd[grnum] = wordsout

                if score >  border:

                    pattkey = str(sorted(patt.values()))
                    if gr.kwpatt.has_key(pattkey): gr.kwpatt[pattkey][1] += friq
                    else:
                        gr.kwpatt[pattkey] = [patt, friq]
                        gr.unchecked_patts.add(pattkey)

        #clear_unpopular_group_patterns(Mg)

        Mg_AddWd = {"Mg": Mg, "additional_wd": additional_wd}

    return Mg_AddWd

