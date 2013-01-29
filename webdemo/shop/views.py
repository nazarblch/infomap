#!/usr/bin/python
# -*- coding: utf-8 -*-
from ast import literal_eval


from appcommon.view import profile

from shop.models import ShopInfo, Products, Categories, Vendors
from agency.models import Clients

from shop.xl import *
from django.http import  HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from yafunc import  wordstat
from shop.groupModels import *
from shop.groups import *

from cv_syn.synonyms import *
from project.views import get_default_info
from settings import YML_UPLOAD_PATH
from shop.functions import save_upload
from project.keywords.modsyn_for_group import Mg_for_vendor_category, wordstat_first_request, wordstat_next_request

from shop.groupModels import Foursquare
from django.core.cache import cache


prefilter_function = get_default_info



def index(request, sid = None):
    if 'client' not in request.session:
        request.session['client'] = 1

    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login

    if request.POST.has_key("sid"):
        sid = int(request.POST["sid"])

    if sid is not None:
        request.session["shop"] = ShopInfo.objects.get(id=int(sid))

    if "shop" in request.session and request.session["shop"].client != cl:
        del request.session["shop"]

    if "shop" not in request.session:
        request.session["shop"] = ShopInfo(name = "def", company = "def", url = "def", email = "def", client=cl)
        request.session["shop"].save()

    shopid = request.session["shop"].id
    shopname = request.session["shop"].name

    other_shops = cl.shopinfo_set.all()

    return render(request, 'shop/index.html', {
        "cllogin": cllogin,
        "shopid": shopid,
        "clid": clid,
        "shopname": shopname,
        "username": request.user.username,
        "shopobj": request.session["shop"],
        "other_shops": other_shops
    })





def add_syn_vendor_category(request, templ_dict, shopobj):

	

    categories = shopobj.categories.all()
    vendors = shopobj.vendors.all()


    if categories.count() == 0:
        return HttpResponse("Shop doesn't have any categories!")
    if vendors.count() == 0:
        return HttpResponse("Shop doesn't have any vendors")


    db_category_syn = categories[0].category_synonyms_set.all()

    ob=Category_synonyms(categories[0].name)
    ob.phr_mod10 += [syn.name for syn in db_category_syn]
    ob.obtained_phr |= set([syn.name for syn in db_category_syn])

    ob.phrase_suggestion_recursive( 10, [])

    request.session["cur_cv_ob"] = ob
    request.session["cv_obs"] = {}


    ya_category_syn = ob.phr_div10



    if type(ya_category_syn) == type(""):
        return HttpResponse("Direct error: " + str(ya_category_syn))

    db_category_syn = [syn.name for syn in db_category_syn]
    ya_category_syn = set(ya_category_syn) - set(db_category_syn)



    first_elem = categories[0]
    request.session["cv_obs"]["cat"+str(first_elem.id)] = ob

    templ_dict.update({
        "first_elem": first_elem,
        "categories":categories,
        "vendors":vendors,
        "db_category_syn":db_category_syn,
        "ya_category_syn":ya_category_syn
    })


    return render_to_response("shop/add_syn_vendor_category.html", templ_dict)





# ============================================
#          model synonyms
# ============================================



# return {"Mg": Mg, "vendor": VENDOR, "category": CATEGORY}
# Mg - array of ModelGroup classes (groupModels.py)
def kw_phrases(request):

    if 'client' not in request.session:
        return HttpResponse("Client hasn't been defined")

    if 'shop' not in request.session:
        return HttpResponse("Shop hasn't been defined")



    def_templ_data = get_default_info(request)

    templ_dict = {}
    templ_dict.update(def_templ_data)

    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shop = request.session["shop"]
    shopname = shop.id

    if 'category' not in request.session or 'vendor' not in request.session:
        request.session['category'] = shop.categories.all()[0]
        request.session['vendor'] = request.session['category'].vendors.all()[0]

    vendor = request.session['vendor']
    category = request.session['category']

    VENDOR = vendor.name
    CATEGORY = category.name

    products = shop.products_set.filter(category=category, vendor=vendor)

    list_models=[model(prod.model, prod.id) for prod in products]


    if len(list_models) == 0:
        return next_vc(request)


    list_gr=make_group(list_models)

    Mg = [ ModelGroup(gr) for gr in list_gr  ]

    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)

    request.session["Mg"] = Mg

    templ_dict.update({"Mg": Mg, "vendor": VENDOR, "category": CATEGORY})

    return render_to_response("shop/kw_phr_simple.html", templ_dict)


# goes to the next vc pair in model syn generation
# return {"Mg": Mg, "vendor": VENDOR, "category": CATEGORY}
def next_vc(request):

        shop = request.session['shop']

        if 'category' not in request.session or 'vendor' not in request.session:
            return  HttpResponse("Category or vendor isn't defined")
        else:
            ven = request.session['vendor']
            cat = request.session['category']

            try:
                vens = cat.vendors.all()
                for i,v in enumerate(vens):
                    if v == ven: request.session['vendor'] = vens[i+1]

            except:
                try:
                    cats = shop.categories.all()

                    cats_count = len(cats)
                    for i,c in enumerate(cats):
                        if c == cat and i+1 < cats_count: request.session['category'] = cats[i+1]
                        else: del request.session['category']


                except:
                    del request.session['category']

            return kw_phrases(request)








def foursquares(request, templ_dict, shopobj):

    if 'category' not in request.session or 'vendor' not in request.session or request.session['category'] is None \
    or request.session['vendor'] is None:
        request.session['category'], request.session['vendor'] = shopobj.get_first_cat_ven()


    vendor = request.session['vendor']
    category = request.session['category']


    Mg = cache.get('Mg')

    if Mg is None:
        Mg = Mg_for_vendor_category(shopobj, category, vendor)
        Mg = wordstat_first_request(Mg, shopobj, category, vendor)['Mg']
        cache.set('Mg', Mg, 1)

    foursquares_dict = {}

    request.session['model_syns'] = set()
    model_syns = request.session['model_syns']

    for gr_num, gr in enumerate(Mg):
        gr.gen_model_syns()
        foursquares_dict[str(gr_num)] = {}

        for patt_key in gr.get_patt_keys():
            foursquares_dict[str(gr_num)][patt_key] = Foursquare(gr, gr_num, patt_key, model_syns)

    request.session["Mg"] = Mg
    templ_dict["Mg"]=Mg
    request.session['4sqs'] = foursquares_dict
    request.session['model_syns'] = model_syns

    templ_dict['4sqs'] = foursquares_dict

    request.session['shift'] = 0

    return render_to_response('shop/kw_from_foursquares.html', templ_dict)






