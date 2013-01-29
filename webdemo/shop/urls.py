from django.conf.urls import patterns


urlpatterns = patterns('shop',
    (r'^$', 'views.index'),
    (r'^index/(?P<sid>\d+)/$', 'views.index'),
    (r'^ajax_upload/$', 'ajax.ajax_upload'),
    (r'^update_shopinfo/$', 'ajax.update_shopinfo', {"shopobj": None}),

    (r'^addproducts_todb/$', 'ajax.addproducts_todb'),
    (r'^modify_model/$', 'ajax.modify_model'),
    (r'^del_unchecked_products/$', 'ajax.del_unchecked_products'),
    (r'^synonyms/$', 'views.add_syn_vendor_category', {"templ_dict": None, "shopobj": None}),
    (r'^get_syn/$', 'ajax.get_syn'),
    (r'^get_more_syn/$', 'ajax.get_more_syn'),
    (r'^set_syn/$', 'ajax.set_syn',  {"shopobj": None}),
    (r'^change_cur_cv_ob/$', 'ajax.change_cur_cv_ob'),

    (r'^kw_phrases/$', 'views.kw_phrases'),
    (r'^fix_groups/$', 'ajax.fix_groups'),
    (r'^synforall/$', 'ajax.synforall'),
    (r'^synforall_sep/$', 'ajax.synforall_sep'),
    (r'^show_model_syns/$', 'ajax.show_model_syns'),
    (r'^push_model_syns_to_db/$', 'ajax.push_model_syns_to_db'),
    (r'^next_vc/$', 'views.next_vc'),
    (r'^foursquares/$', 'views.foursquares', {'templ_dict': None, 'shopobj': None}),
    (r'^wordstat_next/$', 'ajax.wordstat_next', {'vendor': None}),
    (r'^foursquare_next/$', 'ajax.foursquare_next'),
    (r'^foursquares_save/$', 'ajax.foursquares_save', {"shopobj": None}),

)


