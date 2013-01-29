# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from appcommon.view import get_default_info
from project.models import *
from project.kw_group import Kw_net
from shop.models import ShopInfo


prefilter_function = get_default_info



def budget(request, templ_dict, shopobj):


    if request.method == "POST":

        kwnet = request.session["kwnet"]

        if request.POST.has_key("accept"):
            kwnet.save_state()
            HttpResponseRedirect("/project/companies")

        elif request.POST.has_key("reload"):

            kwnet.set_budget(request.POST["budget"])

    else:

        prod_groups = shopobj.make_companies("category", "vendor")
        budget = 1000


        price_names = {1:'Min', 2:'Max', 3:'PremiumMin'}
        preficses = {1:'', 2:'FirstPlace', 3:'Premium'}

        kwnet = Kw_net(prod_groups, budget, price_names, preficses)


    request.session["kwnet"] = kwnet

    templ_dict.update({"kwnet": kwnet})

    return render(request, "project/budget.html", templ_dict)




def banners(request, templ_dict, shopobj):

    #bi-graph of kws and products
    #contains pr_groups array one for each ven/cat
    #kwnet = request.session["kwnet"]

    categories = shopobj.categories.all()
    vendors = shopobj.vendors.all()

    # already created banners
    banners_per_cat_ven = dict([ ( c.id, {}) for c in categories ])

    cat, ven = shopobj.get_first_cat_ven()

    while True:

        banners = Banner.objects.filter(product__shop = shopobj, product__vendor = ven, product__category = cat )
        banner_tmls = Banner_template.objects.filter(id__in = [b.id for b in banners])

        banners_per_cat_ven[cat.id][ven.id] = banner_tmls

        cat, ven = shopobj.get_next_cat_ven(cat, ven)

        if cat is None or ven is None:
            break

    templ_dict["categories"] = categories
    templ_dict["vendors"] = vendors
    templ_dict["banners_per_cat_ven"] = banners_per_cat_ven


    return render_to_response('project/banner/banners.html', templ_dict)
