#!/usr/bin/python
# -*- coding: utf-8 -*-
from ast import literal_eval
import json

from shop.models import  Products, Categories, Vendors

from shop.xl import *
from django.http import  HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, render
from yafunc import  wordstat
from shop.groupModels import *
from shop.groups import *

from cv_syn.synonyms import *
from project.views import get_default_info
from settings import YML_UPLOAD_PATH
from shop.functions import save_upload
from project.keywords.modsyn_for_group import  wordstat_next_request

from shop.groupModels import Foursquare


prefilter_function = get_default_info


# ============================================
#           products uploading
# ============================================


def ajax_upload( request ):

        upload = request
        is_raw = True
        try:
            filename = request.GET[ 'qqfile' ]
        except KeyError:
            return HttpResponseBadRequest( "AJAX request not valid" )


        success = save_upload( upload, filename, is_raw, request )

        ret_json = { 'success': success, }
        return HttpResponse( json.dumps( ret_json ) )



def addproducts_todb(request):

        from functions import download

        yml_name = request.POST["ymlfile"]
        localpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), YML_UPLOAD_PATH + str(yml_name).split('/')[-1])


        if "ymlfile" in request.session:
            ymlfile = request.session["ymlfile"]
            del request.session["ymlfile"]

        elif re.match("^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$", yml_name) is not None:
            try:
                download(yml_name, localpath)
                ymlfile = localpath
            except IOError, e:
                print  e
                return HttpResponse("YMLError: " + str(e))
        else:
            return HttpResponse("YMLError: yml file hasn't been uploaded")


        ymltype = request.POST["ymltype"]


        shopobj = request.session["shop"]

        fparams = ["category", "vendor"]
        shop_id = shopobj.id


        try:
            if ymltype == "xml":

                shop = YML(ymlfile, shopobj)
                shop.setdbdata()

            elif ymltype == "xl":

                shop = XL(ymlfile, shopobj)


        except YMLError, e:
            return HttpResponse("YMLError "+str(e))

        except Exception, e:
            return HttpResponse("Other Error "+str(e))

        else:

            request.session["shop"] = shopobj

            try:
                pr_blocks = shopobj.make_companies(*fparams)

            except Exception, e:
                return HttpResponse("Failed to make product blocks " + str(e))


            return render_to_response("shop/show_companies.html", {"pr_blocks":pr_blocks,"fparams":fparams})



def modify_model(request):


        if "shop" not in request.session:
            return HttpResponse("Shop isn't defined")

        shopobj = request.session["shop"]

        pr_id = int(request.POST["pr_id"]) or None
        pr_field = str(request.POST["pr_field"]) or None
        pr_new_val = str(request.POST["new_val"]).strip() or None

        PR_FIELDS = ["model", "price", "typePrefix"]

        if not str(pr_id).isdigit() or pr_field not in PR_FIELDS and pr_new_val != None:
            return HttpResponse("Wrong post data")

        try:
            product = Products.objects.get(id=pr_id)
        except:
            return HttpResponse("Product doesn't exist id="+str(pr_id))

        if product.shop != shopobj:
            return HttpResponse("Product isn't yours")

        try:
            product.__setattr__(pr_field, pr_new_val)
            product.save()
        except:
            return HttpResponse("Wrong modified value")


        return HttpResponse("1")




def del_unchecked_products(request):


        if "shop" not in request.session:
            return HttpResponse("Shop isn't defined")

        shopobj = request.session["shop"]

        try:

            if len(request.POST["unchecked_ids"]) == 0 : return HttpResponse("1")

            postarr = str(request.POST["unchecked_ids"]).strip().split(',')

            postarr = map(lambda i: int(i), postarr)

            Products.objects.filter(shop = shopobj, id__in = postarr).delete()

        except Exception, e:
            return HttpResponse("Wrong product numbers for deleting "+str(e))


        return HttpResponse("1")


def update_shopinfo(request, shopobj):

    res = []

    sh_attrs = ["name", "url", "company", "email"]

    for attr in sh_attrs:
        if request.POST["shopobj_"+attr] != getattr(shopobj, attr):
            res.append(getattr(shopobj, attr) +" -> "+request.POST["shopobj_"+attr])

        setattr(shopobj, attr, unicode(request.POST["shopobj_"+attr]))

    shopobj.save()

    request.session["shop"] = shopobj

    return HttpResponse(",".join(res))




# ============================================
#          vendor category synonyms
# ============================================


def change_cur_cv_ob(request):

        ob = request.session["cur_cv_ob"]
        dbtable = request.POST['dbtable']

        if ob.dbtable == "cat":
            ob.unchecked_words |= set(request.POST["new_unchecked_words"].strip().split("&_&"))
        obname = request.POST["ob_name"]

        try:
            request.session["cur_cv_ob"] = request.session["cv_obs"][obname]
        except:
            get_syn(request)

        return HttpResponse(obname)


def get_syn(request):

    if request.is_ajax():
        dbtable = request.POST['dbtable']
        id = int(request.POST['id'])

        ob = request.session["cur_cv_ob"]

        if "new_unchecked_words" in request.POST and ob.dbtable == "cat":
            ob.unchecked_words |= set(request.POST["new_unchecked_words"].strip().split("&_&"))



        ya_syn = ""

        if dbtable == 'cat':

            obj = Categories.objects.get(id=id)
            db_syn = obj.synonyms_names_list()
            name = obj.name

            ob=Category_synonyms(name)
            ob.phr_mod10 += db_syn
            ob.obtained_phr |= set(db_syn)

            ob.phrase_suggestion_recursive( 10, [])

            request.session["cur_cv_ob"] = ob

            ya_syn = ob.phr_div10

            request.session["cv_obs"]["cat"+str(id)] = ob

        if dbtable == 'ven':
            obj = Vendors.objects.get(id=id)
            db_syn = obj.synonyms_names_list()
            name = obj.name


            ob=Vendor_synonyms(name, method='sug')


            ya_syn = ob.synonyms
            ya_syn = set(ya_syn) - set(db_syn)
            request.session["cur_cv_ob"] = ob
            request.session["cv_obs"]["ven"+str(id)] = ob



        if type(ya_syn) == type(""):
            return HttpResponse("Direct error: " + str(ya_syn))


        return render_to_response("shop/syn_container.html", {
            "db_syn":db_syn,
            "ya_syn":ya_syn})

def get_more_syn(request):


        ob = request.session["cur_cv_ob"]

        dbtable = request.POST['dbtable']

        if dbtable == 'cat':

            if "new_unchecked_words" in request.POST:
                ob.unchecked_words |= set(request.POST.getlist("new_unchecked_words"))

            checked_phr = []
            if "checked_phr" in request.POST:
                checked_phr = request.POST.getlist("checked_phr")

            ob.phrase_suggestion_recursive( 10, [], checked_phr)

            ya_syn = ob.phr_div10

        if dbtable == 'ven':

            ya_syn = ob.add_wordstat()



        request.session["cur_cv_ob"] = ob

        return render_to_response("shop/syn_container.html", {
            "db_syn":[],
            "ya_syn":ya_syn})







def set_syn(request, shopobj):

        cat_syns = literal_eval(request.POST.get('cat_syn', "{}"))
        ven_syns = literal_eval(request.POST.get('ven_syn', "{}"))


        shopobj.setCatSyns(cat_syns)
        shopobj.setVenSyns(ven_syns)


        return  HttpResponse("0")





# ============================================
#          model synonyms
# ============================================


# creates Mg from drag and drop tables
def fix_groups(request):



        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session["shop"]

        modnumarr = request.POST['modnumarr']

        Mg = makeMg_from_ajax(request.POST, modnumarr)

        request.session["Mg"] = Mg

        return render_to_response("shop/kw_phrases_container.html", {"Mg": request.session["Mg"]})



# add to Mg  model patterns from wordstat
def synforall(request):


        if 'shift' in request.session:
            del request.session['shift']

        Mg = request.session["Mg"]

        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session['shop']

        VENDOR = vendor.name
        ven_syn = shop.vendor_syns.filter(vendor=vendor)
        CATEGORY = category.name
        cat_syn = shop.category_syns.filter(category=category)

        req_phrs = make_ven_cat_syn_phrs(VENDOR, CATEGORY, ven_syn, cat_syn)

        firstphrases = wordstat(req_phrs[:10], showsmax=20000, geos = [1,2])[0]

        additional_wd = set()

        Mg = filter(lambda gr: len(gr.models)>0 , Mg)

        for phrasesarr in firstphrases:
            for phr in phrasesarr:
                num,wordsoutset = find_nearest_groups(Mg, phr, 0.2)
                for addwd in wordsoutset:
                    additional_wd.add(addwd)

        request.session["Mg"] = Mg


        return render_to_response("shop/ya_kw_container.html", {"Mg": Mg, "additional_wd": additional_wd})




# updates Mg with new model patterns from wordstat
def synforall_sep(request, border=0.19):


        Mg = request.session["Mg"]

        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session['shop']

        VENDOR = vendor.name

        if "shift" not in request.session:
            request.session['shift'] = 0
        else:
            request.session['shift'] += 1

        shift = request.session['shift']
        phr_gr_nums = get_popul_gr_phrs(Mg, shift, [VENDOR])

        if len(phr_gr_nums) == 0:
            return render_to_response("shop/ya_kw_container.html", {"Mg": Mg, "additional_wd": {} })


        req_phrs = phr_gr_nums.keys()

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
                        else: gr.kwpatt[pattkey] = [patt, friq]




        request.session["Mg"] = Mg


        return render_to_response("shop/ya_kw_container.html", {"Mg": Mg, "additional_wd": additional_wd})



# returns template with model synonyms
def show_model_syns(request):

        Mg = request.session["Mg"]

        shop = request.session['shop']

        for k,gr in enumerate(Mg):
            kw_patts = request.POST.get(str(k),"")
            if kw_patts == "": continue

            kw_patts = kw_patts.split("_")

            for kw_patt in kw_patts:
                for mod in gr.models:
                    modkwphr = mod.get_subphrathe(gr.kwpatt[str(kw_patt)][0], gr.pattern)
                    if len(modkwphr) > 0:
                        mod.kwphr.add(" ".join(modkwphr))

        request.session["Mg"] = Mg

        return render_to_response("shop/gr_kw_final_container.html", {"Mg": Mg})


# save new model synonyms from ajax post request
def push_model_syns_to_db(request):

        Mg = request.session["Mg"]

        shop = request.session['shop']

        try:

            for k,gr in enumerate(Mg):
                for mod in gr.models:

                    mod_syns = []
                    if str(mod.id) not in request.POST: continue
                    else: mod_syns = request.POST[str(mod.id)].strip(',').split(',')
                    if len(mod_syns) == 0: continue

                    mod_syns = map(lambda s: str(s).strip(), mod_syns)

                    product = Products.objects.get(id=mod.id)
                    product.add_synonyms(mod_syns)

        except Exception, e:
            print str(e)
            return  HttpResponse(str(e))



        return  HttpResponse("0")





def wordstat_next(request, vendor):


        shift = request.session['shift']
        Mg = request.session['Mg']


        wordstat_request = wordstat_next_request(vendor, shift, Mg)

        if wordstat_request is None:
            return HttpResponse('-1')


        if wordstat_request == -1:
            return HttpResponse('-1')

        else:
            request.session["Mg"] = wordstat_request['Mg']
            request.session['shift'] += 1

            return HttpResponse('0')



def foursquare_next(request):


        dict3 = literal_eval(request.POST['4sqs'])
        Mg = request.session['Mg']
        model_syns = request.session['model_syns']

        foursquares_dict =request.session['4sqs']

        for gr_num, gr in enumerate(Mg):
            gr.gen_model_syns()

            for patt_key in gr.get_patt_keys():

                if not foursquares_dict[str(gr_num)].has_key(patt_key):
                    foursq = Foursquare(gr, gr_num, patt_key, model_syns)
                    foursquares_dict[str(gr_num)][patt_key] = foursq

                    if foursq.empty():
                        foursq.update_patt_kw({})


                elif dict3.has_key(str(gr_num)) and dict3[str(gr_num)].has_key(patt_key):
                    Fsqr = foursquares_dict[str(gr_num)][patt_key]
                    Fsqr.update_patt_kw(dict3[str(gr_num)][patt_key])



        request.session['model_syns'] = model_syns
        request.session['4sqs'] = foursquares_dict

        templ_dict = {'4sqs': foursquares_dict}

        return render(request, 'shop/_foursq_next.html', templ_dict)




def foursquares_save(request, shopobj):


        foursquares_dict = request.session['4sqs']
        Mg = request.session['Mg']
        dict3 = literal_eval(request.POST['4sqs'])


        for gr_num, gr in enumerate(Mg):

            for patt_key in gr.get_patt_keys():

                if dict3.has_key(str(gr_num)) and dict3[str(gr_num)].has_key(patt_key):
                    Fsqr = foursquares_dict[str(gr_num)][patt_key]
                    Fsqr.update_patt_kw(dict3[str(gr_num)][patt_key])



        global_model_syn_dict = dict()

        for gr_num in foursquares_dict.keys():

            for patt_key in foursquares_dict[str(gr_num)].keys():

                foursq = foursquares_dict[str(gr_num)][patt_key]

                modsyn_foursq_dict = foursq.create_modsyn_dict()
                global_model_syn_dict.update(modsyn_foursq_dict)


        for gr_num, mg in enumerate(Mg):
            mg.create_all_modsyns_keywords(global_model_syn_dict, foursquares_dict[str(gr_num)].keys())
            mg.create_all_model_keywords()


        # next vc

        cur_ven = request.session['vendor']
        cur_cat = request.session['category']

        request.session['category'], request.session['vendor'] = shopobj.get_next_cat_ven(cur_cat, cur_ven)

        return HttpResponse("0")