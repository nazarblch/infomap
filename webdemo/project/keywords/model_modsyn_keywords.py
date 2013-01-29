

class PrModel:
    def __init__(self):
        pass

    def get_category(self):
        pass

    def get_vendor(self):
        pass


    def get_product(self):
        pass

    def get_shop(self):
        pass


    def keywords_from_patterns(self, patterns_dict, Keyword):

        for patt in patterns_dict.keys():
            if patterns_dict[patt] == 1:

                if patt == 'cvm':
                    for cat_syn in self.get_category().synonyms(self.get_shop() ,with_self=True):
                        for ven_syn in self.get_vendor().synonyms(self.get_shop(), with_self=True):
                            kw = Keyword({'product': self.get_product(), 'words': [cat_syn, ven_syn, self]})
                            kw.save()

                elif patt == 'cm':
                    for cat_syn in self.get_category().synonyms(self.get_shop(), with_self=True):
                        kw = Keyword({'product': self.get_product(), 'words': [cat_syn, self]})
                        kw.save()

                elif patt == 'vm':
                    for ven_syn in self.get_vendor().synonyms(self.get_shop(), with_self=True):
                        kw = Keyword({'product': self.get_product(), 'words': [ ven_syn, self]})
                        kw.save()

                elif patt == 'm':
                    kw = Keyword({'product': self.get_product(), 'words': [self]})
                    kw.save()