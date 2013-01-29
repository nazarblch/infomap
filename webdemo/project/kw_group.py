# -*- coding: utf-8 -*-
from copy import deepcopy
from itertools import groupby
from math import fsum
from appcommon.functions import map_dict

from project.models import Keyword
from yafunc import budget_forecast
from django.core.cache import cache



class node:

    def __init__(self, id, obj, edges):

        self.id = id
        self.obj = obj
        self.edges = edges

        self.accepted = False
        self.forecast = {"price": 0, "clicks": 0, "sum": 0}
        self.profit = 0.0


    def add_link(self, obj_key):

        self.edges.add(obj_key)


    def clicks_score(self):

        if  not self.forecast["clicks"]:
            return 0.0

        return self.forecast["clicks"]/self.weight()


    def profit_score(self):

        if  not self.forecast["clicks"] or not len(self.edges):
            return 0.0

        if not self.profit:
            self.profit = fsum([e.obj.price  for e in self.edges ]) / len(self.edges)

        return (self.profit * self.forecast["clicks"]) / self.weight()


    def kw_score(self, goal_func):

        if self.forecast["ctr"] < 0.5:
            return 0

        return getattr(self, goal_func) ()



    def weight(self):

        return self.forecast['sum']




    def __unicode__(self):
        return u'%s' % self.obj.get_name()

    def __str__(self):
        return self.obj.get_name()







class Kw_net:

    def __init__(self, pr_blocks, budget, price_names, prefixes):

        if price_names.keys() != prefixes.keys():
            raise Exception("price_names should have the same keys as prefixes")


        self.budget = budget
        self.price_names = price_names
        self.prefixes = prefixes

        self.kws = {}
        self.kw_phr_blocks = {}

        self.prods = {}
        self.pr_groups = []

        for block_num, block in enumerate(pr_blocks):

            block_pr_ids, prod_nodes = self.set_prod_nodes(block["products"])
            self.pr_groups.append(
                Kw_group(
                    block["category"],
                    block["vendor"],
                    prod_nodes,
                    self
                )
            )

            kw_in_block = self.extract_kw_per_block(block)


            for kw in kw_in_block:

                kw_links = kw.product.filter(id__in = block_pr_ids)

                kw_nodes = self.set_kw_nodes(kw)

                self.add_links(kw_nodes, kw_links)


        phrases = self.get_phrases()


        forecast_dict = cache.get('forecast_dict')

        if forecast_dict is None or len(forecast_dict) != len(phrases):
            forecast_dict = budget_forecast(phrases)
            cache.set('forecast_dict', forecast_dict, 500*60*60)


        self.set_kw_forecast(forecast_dict)

        self.optimize()



    def set_budget(self, value):

        self.budget = int(value)

        self.optimize()


    def optimize(self):

        self.push_into_pack()

        self.set_prod_forecast()

        for gr in self.pr_groups:
            gr.sum_prod_budget()
            gr.optimize_profit()

        self.set_prod_forecast()

        for gr in self.pr_groups:

            gr.sum_prod_profit()



    def set_kw_forecast(self, forecast_dict):

        for phr, data in forecast_dict.items():

            for label_num, label in self.price_names.items():

                pref = self.prefixes[label_num]

                kw_key  = unicode(phr) + '_' + unicode(label)
                kw_node = self.kws[kw_key]

                kw_node.forecast = {

                    "price": float(data[label]),
                    "ctr": float(data[pref+"CTR"]),
                    "clicks": int(data[pref+"Clicks"]),
                    "sum": float(data[pref+"Clicks"])*float(data[label]),
                    "position": unicode(label)

                }





    def add_links(self, nodes, links):

        for kw_node in nodes:
            for pr_link in links:

                if self.prods.has_key(pr_link.id):

                    prod_node = self.prods[pr_link.id]

                    prod_node.add_link(kw_node)
                    kw_node.add_link(prod_node)



    def set_prod_nodes(self, products):

        ids = []
        prod_nodes = []

        for prod in products:

            prod_node = node(prod.id, prod, set())
            self.prods[prod.id] = prod_node
            ids.append(prod.id)
            prod_nodes.append(prod_node)

        return ids, prod_nodes





    def set_kw_nodes(self, kw):

        res = []

        for label in self.price_names.values():

            kw_key  = unicode(kw.get_name()) + '_' + unicode(label)

            if not self.kws.has_key(kw_key):

                kw_node = node(kw_key, kw, set() )
                self.kws[kw_key] = kw_node

            else:
                kw_node = self.kws[kw_key]


            res.append(kw_node)

        self.kw_phr_blocks[unicode(kw.get_name())] = res

        return res




    def extract_kw_per_block(self, block):

        kw_in_block = Keyword.objects.filter(
            category = block["category"] ,
            vendor = block["vendor"],
            product__in = block["products"]
        )

        return kw_in_block




    def get_phrases(self):

        res = set()

        for kw_key, kw_node in self.kws.items():

            res.add(unicode(kw_node))

        return res


    def drop_nodes(self):

        for kw_key, kw_node in self.kws.items():
            kw_node.accepted = False


    def push_into_pack(self, goal_func = "clicks_score", budget = None):

        if not budget:
            budget = self.budget

        self.drop_nodes()

        def cmp_blocks(block1, block2):

            sc1 = -block1[-1].kw_score(goal_func)
            sc2 = -block2[-1].kw_score(goal_func)

            if sc1 != sc2:
                return cmp(sc1, sc2)
            else:
                return cmp(-block1[-1].forecast["ctr"], -block2[-1].forecast["ctr"])


        phr_blocks = map(
            lambda block: sorted(block, key = lambda obj: obj.kw_score(goal_func) ),
            self.kw_phr_blocks.values()
        )

        phr_blocks.sort(cmp = cmp_blocks)

        sumW = 0.0

        for block in phr_blocks:

            max_node = block[-1]

            sumW += max_node.weight()

            if sumW >= budget:
                sumW -= max_node.weight()
                break

            max_node.accepted = True


        return  sumW


    def set_prod_forecast(self, gr = None):

        if not gr:
            pr_arr = self.prods.values()
        else:
            pr_arr = gr.products

        for prod in pr_arr:

            prod.forecast["clicks"] = 0
            prod.forecast["sum"] = 0

            for kw_node in prod.edges:

                if not kw_node.accepted:
                    continue

                prod.forecast["clicks"] += kw_node.forecast["clicks"]/len(kw_node.edges)
                prod.forecast["sum"] += kw_node.forecast["sum"]/len(kw_node.edges)

            if prod.forecast["clicks"] > 0:
                prod.forecast["price"] = prod.forecast["sum"] / prod.forecast["clicks"]


    def save_state(self):
        pass




class Kw_group:

    def __init__(self, cat, ven, products, G):

        self.G = G

        self.ven = ven
        self.cat = cat
        self.products = products
        self.keywords = set()

        self.clicks = None
        self.avg_click_price = None
        self.budget = 0


    def set_budget(self, value):

        self.budget = value
        self.optimize_profit()


    def sum_prod_budget(self):

        self.budget = 0

        for prod in self.products:
            self.budget += prod.forecast["sum"]


    def sum_prod_profit(self):

        self.profit = 0

        for prod in self.products:
            self.profit += prod.forecast["clicks"]*prod.obj.price



    def gather_kw_nodes(self):

        for pr_node in self.products:

            self.keywords.update(pr_node.edges)


    def get_phrases(self):

        return map(unicode, self.keywords)


    def get_kw_phr_blocks(self):

        res = []

        for key, group in groupby(self.keywords, unicode):
            res.append(list(group))

        return res


    def set_prod_forecast(self):
        self.G.set_prod_forecast(self)


    def drop_nodes(self):

        for kw_node in self.keywords:
            kw_node.accepted = False


    def optimize_profit(self, goal_func="profit_score"):

        if not len(self.keywords):
            self.gather_kw_nodes()

        if not self.budget:
            self.sum_prod_budget()

        self.drop_nodes()

        def cmp_blocks(block1, block2):

            sc1 = -block1[-1].kw_score(goal_func)
            sc2 = -block2[-1].kw_score(goal_func)

            if sc1 != sc2:
                return cmp(sc1, sc2)
            else:
                return cmp(-block1[-1].forecast["ctr"], -block2[-1].forecast["ctr"])


        phr_blocks = map(
            lambda block: sorted(block, key = lambda obj: obj.kw_score(goal_func) ),
            self.get_kw_phr_blocks()
        )

        phr_blocks.sort(cmp=cmp_blocks)

        sumW = 0.0

        for block in phr_blocks:

            max_node = block[-1]

            sumW += max_node.weight()

            if sumW >= self.budget:
                sumW -= max_node.weight()
                break

            max_node.accepted = True


        self.budget = sumW


        return  sumW




