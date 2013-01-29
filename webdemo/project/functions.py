from math import fsum
from copy import deepcopy


class Item:
    def __init__(self, weight, cost, ind = None):
        self.ind = ind
        self.weight = weight
        self.cost = cost

    def __str__(self):
        res =  '('
        if self.ind is not None:
            res += str(self.ind) + "|"
        res += str(self.weight) + ':' + str(self.cost) + ')'

        return res

class ItemGroup:
    def __init__(self, it_arr):
        self.items = it_arr


class Solution:

    def __init__(self, items):
        self.items = items

        self.weight = fsum([item.weight for item in items])
        self.cost = fsum([item.cost for item in items])


    def additem(self, item):
        new_S = deepcopy(self)

        new_S.items.append(item)
        new_S.weight += item.weight
        new_S.cost += item.cost

        return new_S


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


def add_solution_to_paretoSet(solAdd, pSet):

    new_pSet = []

    for s in pSet:

        if s.weight <= solAdd.weight and s.cost > solAdd.cost:
            return pSet

        if not (solAdd.weight <= s.weight and s.cost > solAdd.cost):




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

def is_group(itemOrGroup):

    return isinstance(itemOrGroup, list) or isinstance(itemOrGroup, set)

def KnapsackNemhauserUllman(items, B):
    pareto = [Solution([])]

    for itemOrGroup in items:
        news = []
        for solution in pareto:

            if is_group(itemOrGroup):
                for item in itemOrGroup:
                    if solution.weight + item.weight <= B:
                        news.append( solution.additem(item) )

            else:
                if solution.weight + itemOrGroup.weight <= B:
                    news.append( solution.additem(itemOrGroup) )

        pareto = merge_item_sets(pareto, news)

    return pareto[-1], len(pareto)




def test():
    items = [
             [Item(8, 8.1, 1), Item(9,10, 1), Item(10,11, 1)] ,
             [Item(8,8, 2), Item(8,8, 2)],
             [Item(9,10, 3), Item(10,11, 3)],
             Item(8,8, 4),
             [Item(8,8, 5), Item(9,10, 5)],
             Item(10,11, 6),
             [Item(8,8, 7), Item(8,8, 7)],
    ]

    sol, sol_count =  KnapsackNemhauserUllman(items, 35.0)

    print sol
    print sol_count


if __name__ == "__main__":
    test()

