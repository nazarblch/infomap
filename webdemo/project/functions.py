from typecheck import *
from math import fsum
from copy import deepcopy




def max_ctr(product):
    return product["ctr"]/product["price"]

def push_into_pack(products, price_names, fref_names, budget, goal_func = max_ctr):
    separated_pr = []
    res = []

    if price_names.keys() != fref_names.keys():
        raise IndexError("price_names should have the same keys as fref_names")

    for pr_num,prod in enumerate(products):

        for num,price_name in price_names.items():
            pref = fref_names[num]

            prod_part = {
                "pr_num":pr_num,
                "price":prod[price_name],
                "price_name":price_name,
                "ctr": prod[pref+"CTR"],
                "clicks": prod[pref+"Clicks"],
                "sum": prod[pref+"Clicks"]*prod[price_name],
                "shows":prod["Shows"]
            }


            separated_pr.append(prod_part)


    separated_pr = filter(lambda p: p["ctr"] > 0.5 ,separated_pr)

    summa = 0.0

    while summa <= budget and len(separated_pr) > 0:
        max = 0
        max_id = None

        for pr_num,prod in enumerate(separated_pr):
            t = goal_func(prod)
            if t > max:
                max = t
                max_id = pr_num

        try:
            pr = separated_pr.pop(max_id)
        except:
            print max_id
            print max
            print separated_pr

        summa += pr["sum"]
        separated_pr = filter(lambda p: p["pr_num"] != pr["pr_num"] ,separated_pr)

        products[pr["pr_num"]]["price_name"] = pr["price_name"]
        products[pr["pr_num"]]["price_val"] = pr["price"]

        res.append( products[pr["pr_num"]] )


    return  summa, res



def rank_products(products, price_names, fref_names, pos_weights):

    def find_best_pr_phr(phrs, k):

        phr_ranks = []

        for phr_num,phr in enumerate(phrs):

            rank = 0

            for num,price_name in price_names.items():
                pref = fref_names[num]
                phr_part = {"pr_num":pr_num, "price":phr[price_name], "price_name":price_name,
                             "ctr": phr[pref+"ctr"], "clicks": phr[pref+"clicks"], "sum": phr[pref+"sum"], "shows":phr["shows"] }

                rank += phr_part['ctr']*pos_weights[price_name]

            phr_ranks.append( (phr_num, phr, rank) )

        phr_ranks = sorted(phr_ranks, key=lambda item: item[2])[:k]

        return phr_ranks



    for prod in products:
        prod_popularity = 0

        best_phrs = find_best_pr_phr(prod['phrs'], 4)






class Item:
    def __init__(self, weight, cost):
        self.weight = weight
        self.cost = cost

    def __str__(self):
        return '(' + str(self.weight) + ':' + str(self.cost) + ')'


class Solution:

    @accepts(Self(), [Item])
    def __init__(self, items):
        self.items = items

        self.weight = fsum([item.weight for item in items])
        self.cost = fsum([item.cost for item in items])

    @accepts(Self(), Item)
    def additem(self, item):
        new_S = deepcopy(self)

        new_S.items.append(item)
        new_S.weight += item.weight
        new_S.cost += item.cost

        return new_S

    @accepts(Self(), Self())
    def __add__(self, other):           # self and other should not have equal items
        new_S = deepcopy(self)
        new_S.items += other.items
        new_S.weight += other.weight
        new_S.cost += other.cost

        return  new_S

    def __str__(self):
        res = str()
        res += "sum weight: " + str(self.weight) + "\n"
        res += "sum cost: " + str(self.cost) + "\n"

        res += '['
        for item in self.items:
            res += str(item)

        res += ']'

        return  res



@accepts([Solution], [Solution])
def merge_item_sets(s1, s2): # merge two not empty solution lists
    i = j = 0
    res = []
    while i <= len(s1) or j <= len(s2):
        if i == len(s1):
            res += s2[j:]   # take mod from second list
            break
        if j == len(s2):
            res += s1[i:]   # take mod from first list
            break

        if s1[i].weight <= s2[j].weight:
            if s1[i].cost > s2[j].cost:
                j += 1
            else:
                res.append(s1[i])
                i += 1
        else:

            if s1[i].cost < s2[j].cost:
                i += 1
            else:
                res.append(s2[j])
                j += 1
    return res



@accepts([Item], float)
def KnapsackNemhauserUllman(items, B):
    pareto = [Solution([])]  # pareto optimised solution

    for item in items:
        news = []
        for solution in pareto:
            if solution.weight + item.weight <= B:
                news.append( solution.additem(item) )

        pareto = merge_item_sets(pareto, news)

    return pareto[-1], len(pareto)




def test():
    items = [Item(8,8.1), Item(9,10), Item(10,11) , Item(8,8), Item(8,8), Item(9,10), Item(10,11) , Item(8,8), Item(8,8), Item(9,10), Item(10,11) , Item(8,8), Item(8,8)]
    sol, sol_count =  KnapsackNemhauserUllman(items, 35.0)

    print sol
    print sol_count




