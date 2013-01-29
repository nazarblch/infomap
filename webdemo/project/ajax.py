from ast import literal_eval
from django.shortcuts import render
from project.models import Banner_template

def optimize_group(request):

    kwnet = request.session["kwnet"]

    gr_id = int(request.POST["gr_id"])
    budget = int(request.POST["budget"])

    gr = kwnet.pr_groups[gr_id]

    gr.set_budget(budget)
    gr.set_prod_forecast()
    gr.sum_prod_profit()

    request.session["kwnet"] = kwnet

    templ_dict = {"group": gr}

    return render(request, "project/_budget_kw_group.html", templ_dict)



def create_banners_from_tml(request):

    tml_obj = Banner_template( Title = request.POST["Title"], Text = request.POST["Text"])
    prod_ids  = literal_eval(request.POST.get('prod_ids', "[]"))

    if len(prod_ids):
        tml_obj.save()
        tml_obj.create_banners(prod_ids)