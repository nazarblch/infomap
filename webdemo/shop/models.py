from django.db import models
from agency.models import Clients
from project.keywords.model_modsyn_keywords import PrModel


class ShopModelsError(Exception):
    """Base class for exceptions in this module."""
    pass


class ShopModelsKeyError(ShopModelsError):
    """Exception raised for errors in the input."""

    def __init__(self, expr, msg):
        ShopModelsError.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return repr(self.msg)











class Vendors(models.Model):
    name = models.CharField(max_length=100)
    vendorCode = models.CharField(max_length=100, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)

    templ_label = 'v'


    def get_name(self):
        return self.name


    def get_vendor(self):
        return self


    def __unicode__(self):
        return self.name

    def add_synonyms(self, phrases):
        ids = []

        for phr in phrases:
            phr = phr.lower()
            old_obj = Vendor_synonyms.objects.filter(name=phr)
            if old_obj.count() == 0:
                if self.name != phr:
                    new_syn = Vendor_synonyms(vendor=self, name=phr, score=1)
                    new_syn.save()
                    ids.append(new_syn)
            else:
                old_obj[0].score += 1
                old_obj[0].save()
                ids.append(old_obj[0])

        return ids

    def synonyms_names_list(self):
        syns = self.vendor_synonyms_set.all()
        return [s.name for s in syns]

    def synonyms(self, shop, with_self = False):

        syns = shop.vendor_syns.filter(vendor = self)
        syns = list(syns)

        if with_self:
            syns.append(self.get_vendor())

        return syns

    def del_synonyms(self):
        self.vendor_synonyms_set.all().delete()

class Vendor_synonyms(models.Model):
    vendor = models.ForeignKey(Vendors)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=1)

    templ_label = 'v'

    def get_name(self):
        return self.name

    def get_vendor(self):
        return self.vendor


    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["-score"]




class Categories(models.Model):
    localId = models.IntegerField()
    name =  models.CharField(max_length=100)
    p = models.ForeignKey("self", null=True, default="self")
    vendors = models.ManyToManyField(Vendors, through="Products")

    templ_label = 'c'

    def get_name(self):
        return self.name

    def get_category(self):
        return self



    def __unicode__(self):
        return self.name

    def getChildren(self):
        return Categories.objects.filter(p = self)

    class Meta:
        ordering = ["name"]

    def add_synonyms(self, phrases):
        ids = []

        for phr in phrases:
            phr = phr.lower()
            old_obj = Category_synonyms.objects.filter(name=phr)
            if old_obj.count() == 0:
                if self.name != phr:
                    new_syn = Category_synonyms(category=self, name=phr, score=1)
                    new_syn.save()
                    ids.append(new_syn)
            else:
                old_obj[0].score += 1
                old_obj[0].save()
                ids.append(old_obj[0])

        return ids

    def synonyms_names_list(self):
        syns = self.category_synonyms_set.all()

        return [s.name for s in syns]


    def synonyms(self, shop, with_self = False):

        syns = shop.category_syns.filter(category = self)
        syns = list(syns)

        if with_self:
            syns.append(self.get_category())

        return syns


    def del_synonyms(self):
        self.category_synonyms_set.all().delete()


class Category_synonyms(models.Model):
    category = models.ForeignKey(Categories)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=1)

    templ_label = 'c'

    def get_name(self):
        return self.name

    def get_category(self):
        return self.category


    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["-score"]



class ShopInfo(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    url = models.URLField()
    agency = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Clients)

    categories = models.ManyToManyField(Categories)
    vendors = models.ManyToManyField(Vendors)

    category_syns = models.ManyToManyField(Category_synonyms)
    vendor_syns = models.ManyToManyField(Vendor_synonyms)

    def __unicode__(self):
        return self.name

    def get_next_cat(self, cur_cat):

        after = False
        res_cat = None

        for cat in sorted(self.categories.all(), key=lambda obj: obj.id):

            if cat == cur_cat:
                after = True
                continue

            if after:
                res_cat = cat

        return res_cat



    def get_first_cat_ven(self):

        cur_cat = self.categories.all()[0]

        shop_vendors = self.vendors.all()
        cat_vendors = cur_cat.vendors.all()

        vendors = sorted(set(shop_vendors) & set(cat_vendors), key=lambda obj: obj.id)

        return cur_cat, vendors[0]



    def get_next_cat_ven(self, cur_cat, cur_ven):

        shop_vendors = self.vendors.all()
        cat_vendors = cur_cat.vendors.all()

        vendors = sorted(set(shop_vendors) & set(cat_vendors), key=lambda obj: obj.id)

        if cur_ven == vendors[-1]:
            cur_cat = self.get_next_cat(cur_cat)
            if not cur_cat:
                return None, None
            cat_vendors = cur_cat.vendors.all()
            vendors = sorted(set(shop_vendors) & set(cat_vendors), key=lambda obj: obj.id)


        after = False
        res_ven = None

        for v in vendors:

            if v == cur_ven:
                after = True
                continue

            if after:
                 res_ven = v
                 break

        return cur_cat, res_ven


    def setCatSyns(self, cat_syns):

        for k, phr_arr in cat_syns.items():
            id = int(k)
            obj = Categories.objects.get(id=id)

            cat_syn_objs = obj.add_synonyms(phr_arr)

            for cat_syn in cat_syn_objs:
                self.category_syns.add(cat_syn)


    def setVenSyns(self, ven_syns):

        for k, phr_arr in ven_syns.items():
            id = int(k)
            obj = Vendors.objects.get(id=id)

            ven_syn_objs = obj.add_synonyms(phr_arr)

            for ven_syn in ven_syn_objs:
                self.vendor_syns.add(ven_syn)




    def make_companies(self, *fparams):



        products = Products.objects.filter(shop = self).order_by(*fparams)
        prods_len = products.count()


        if len(set(fparams) - {"category", "vendor", "typePrefix"}) > 0:
            raise ShopModelsKeyError(str(fparams) ,"ShopInfo:make_companies: wrong fparams")



        prod_arr = []



        def get_params(prod):

            res = []

            for param in fparams:
                res.append(prod.__getattribute__(param))

            return res






        def get_group(ind = 0):

            if ind == prods_len: return -1, [], []

            gr = []

            papams = get_params(products[ind])

            while ind < prods_len and papams == get_params(products[ind]) :

                gr.append(products[ind])
                ind += 1

            return ind, gr, papams





        ind, gr, papams = get_group()

        while ind != -1:

            prod_arr_i = {"products": gr}
            prod_arr_i.update( dict(zip(fparams, papams)) )

            prod_arr.append(prod_arr_i)

            ind, gr, papams = get_group(ind)



        return prod_arr







    def setCategories(self, arr):

        try:
            i = 0
            res_arr = {}
            for node in arr:
                node = node.lower().strip()

                obj = Categories.objects.filter( name = node )
                if obj.count() > 0:
                    res_arr[i] = obj[0]
                    self.categories.add(obj[0])
                else:
                    new_cat = Categories()
                    new_cat.localId = i
                    new_cat.name = node
                    new_cat.p = new_cat
                    new_cat.save()

                    res_arr[i] = new_cat
                    self.categories.add(new_cat)
                i = i + 1

        except Exception, e:
            return False, "Error in shop categories array: " + str(e)

        else:
            return True, res_arr

    def setVendors(self, arr1, arr2):

        try:
            i = 0
            res_arr = {}
            if arr2 == False:
                arr3 = ["" for j in arr1]
            else:
                arr3 = arr2
            for name in arr1:
                name = name.lower().strip()

                obj = Vendors.objects.filter(
                        name = name,
                        country_of_origin = arr3[i]
                )
                if obj.count() > 0:
                    res_arr[i] = obj[0]
                    self.vendors.add(obj[0])
                else:
                    new_vendor = Vendors()
                    new_vendor.name = name
                    new_vendor.country_of_origin = arr3[i]

                    new_vendor.save()
                    res_arr[i] = new_vendor
                    self.vendors.add(new_vendor)
                i = i + 1

        except Exception, e:
            return False, "Error in shop vendors array: " + str(e)

        else:
            return True, res_arr




class Products(models.Model, PrModel):
    shop = models.ForeignKey(ShopInfo)
    category = models.ForeignKey(Categories)
    model = models.CharField(max_length=255)
    available = models.BooleanField(blank=True)
    url = models.URLField(blank=True)
    price = models.FloatField(blank=True)
    currencyId = models.CharField( max_length=5, blank=True)
    vendor = models.ForeignKey(Vendors, blank=True)
    sales_notes = models.CharField(max_length=100, blank=True)
    manufacturer_warranty = models.BooleanField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    typePrefix = models.CharField(max_length=255, blank=True)
    local_delivery_cost =models.IntegerField(blank=True, default=-1)
    delivery = models.BooleanField(blank=True)
    downloadable = models.BooleanField(blank=True)

    date = models.DateTimeField(auto_now_add=True)

    templ_label = 'm'


    def get_name(self):
        return self.model

    def get_category(self):
        return self.category

    def get_vendor(self):
        return self.vendor

    def get_product(self):
        return self

    def get_shop(self):
        return self.shop


    def add_synonyms(self, phrases):
        ids = []

        for phr in phrases:
            phr = phr.strip().lower()
            if phr == "":continue

            old_obj = Product_synonyms.objects.filter(name=phr)
            if old_obj.count() == 0:
                new_syn = Product_synonyms(product=self, name=phr, score=1)
                new_syn.save()
                ids.append(new_syn)
            else:
                old_obj[0].score += 1
                old_obj[0].save()
                ids.append(old_obj[0])

        return ids

    def synonyms(self):
        syns = self.product_synonyms_set.all()

        return [s.name for s in syns]


    def __unicode__(self):
        res = ""
        if self.model:
            res += self.typePrefix+": "
        if self.model:
            res += self.model

        return res

    class Meta:
        ordering = ["category","vendor"]
        unique_together = ("shop", "category", "vendor", "model")



class Product_synonyms(models.Model, PrModel):
    product = models.ForeignKey(Products)
    name = models.CharField(max_length=100)
    patt = models.CharField(max_length=50, blank=True)
    score = models.IntegerField(default=1)

    templ_label = 'm'

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return str(self.name).__hash__()

    def get_name(self):
        return self.name

    def get_category(self):
        return self.product.category

    def get_vendor(self):
        return self.product.vendor

    def get_product(self):
        return self.product

    def get_shop(self):
        return self.product.shop





    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["-score"]

    
class Params(models.Model):
    product = models.ForeignKey(Products)    
    name = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True) 

    data = models.CharField(max_length=255, blank=True)

    
    def __unicode__(self):
        return self.name    
    
    class Meta:
        ordering = ["product"]





