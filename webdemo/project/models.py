# -*- coding: utf-8 -*-
import re

from django.db import models
from shop.models import Products, Vendors, Categories


class ProjectModelsError(Exception):
    """Base class for exceptions in this module."""
    pass



class ProjectModelsKeyError(ProjectModelsError):

    def __init__(self, expr, msg):
        ProjectModelsError.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return repr(self.msg)



class ProjectModelsRelationError(ProjectModelsError):

    def __init__(self, obj, msg):
        ProjectModelsError.__init__(self)
        self.obj = obj
        self.msg = msg

    def __str__(self):
        return "obj="+str(self.obj)+" "+repr(self.msg)


class ProjectModelsKeywordError(ProjectModelsError):

    def __init__(self, obj, msg):
        ProjectModelsError.__init__(self)
        self.obj = obj
        self.msg = msg

    def __str__(self):
        return "obj="+str(self.obj)+" "+repr(self.msg)



class Sell_word(models.Model):

    name = models.CharField(max_length=50)

    templ_label = 's'

    def get_name(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.name




class Keyword(models.Model):

    pattern = models.CharField(max_length=4,  blank=True)
    name = models.CharField(max_length=255,  blank=True)

    product = models.ManyToManyField(Products)

    category = models.ForeignKey(Categories, blank=True)
    vendor = models.ForeignKey(Vendors, blank=True)


    def get_name(self):
        return self.name


    def __init__(self, *args, **kwargs):



        if len(args) > 0 and isinstance(args[0], dict) and args[0].has_key('product'):

            self.adding_product = args[0]['product']
            self.forecast = None

            objects_for_keyword = self.Related_objects(args[0]['words'], self.adding_product)

            kwargs["pattern"] = objects_for_keyword.get_pattern()
            kwargs["name"] = objects_for_keyword.get_kw_name()
            kwargs["category"] = self.adding_product.category
            kwargs["vendor"] = self.adding_product.vendor

            args = ()


        models.Model.__init__(self, *args, **kwargs)



    class Related_objects:

        objects_order = {'c':1, 'v':2, 'm': 3, 's':4 }

        def __init__(self, objs, prod):

            self.objects_dict = dict([  (obj.templ_label, obj) for obj in objs    ])

            self.prod = prod

            if self.objects_dict.has_key("c") and self.objects_dict['c'].get_category() != prod.get_category():
                    raise ProjectModelsRelationError(
                        prod,
                        "Related_objects model's and input categories are different"
                    )

            if self.objects_dict.has_key("v") and self.objects_dict['v'].get_vendor() != prod.get_vendor():
                    raise ProjectModelsRelationError(
                        prod,
                        "Related_objects model's and input vendors are different"
                    )

            if self.objects_dict.has_key("m") and self.objects_dict['m'].get_product() != prod:
                    raise ProjectModelsRelationError(
                        prod,
                        "Related_objects model != prod from input"
                    )


        def get_pattern(self):

            label_arr = sorted(self.objects_dict.keys(), key=lambda l: self.objects_order[l])
            return "".join(label_arr)



        def get_kw_name(self):

            items_arr = sorted(self.objects_dict.items(), key=lambda (l,o): self.objects_order[l])

            names_arr = map(lambda (l,o): o.get_name(), items_arr )

            kw_name = " ".join(re.split(' |-|  ',
                " ".join(names_arr).strip()
            )[:7])

            return kw_name


        def get_category(self):

            return self.prod.get_category()


        def get_vendor(self):

            return self.prod.get_vendor()



    def save(self):

        try:
            Keyword.objects.get(
                name = self.name,
                category = self.category,
                vendor = self.vendor
            ).product.add(self.adding_product)

        except:

            if self.name != "":

                super(Keyword,self).save()
                self.product.add(self.adding_product)

            else:
                raise ProjectModelsKeywordError(self, "save failed")




    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        ordering = ["pattern"]
        unique_together = ("category", "vendor", "name")



class Campaign(models.Model):

    pass



class Banner_template(models.Model):

    Title = models.CharField(max_length=50)
    Text = models.CharField(max_length=140)

    def create_banners(self, prod_ids):

        for pid in prod_ids:

            pid = int(pid)
            product = Products.objects.get(id=pid)

            banner = Banner(product = product, template = self)
            banner.save()



    class Meta:
        unique_together = ("Title", "Text")



class Banner(models.Model):

    campaign = models.ForeignKey(Campaign, blank=True)
    product = models.ForeignKey(Products)

    BannerID = models.IntegerField(unique=True, null=True, blank=True)
    Geo = models.CharField(max_length=50, blank=True)
    Href = models.URLField(blank=True)

    template = models.ForeignKey(Banner_template)



    def get_vendor(self):
        return self.product.get_vendor()

    def get_category(self):
        return self.product.get_category()



class Banner_phrases(models.Model):

    keyword = models.ForeignKey(Keyword)
    banner = models.ForeignKey(Banner)
    price = models.FloatField()

