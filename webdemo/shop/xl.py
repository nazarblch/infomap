#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd


from shop.models import Products, Vendors, Params


try:
    from shop.exeptions import YMLError
except ImportError:
    from shop.exeptions import YMLError



try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                import cElementTree as etree
            except ImportError:
                try:
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Failed to import ElementTree from any known place")

class XL:

    
    def __init__(
            self,
            xlfile,
            shopobj,
            catstag = "categories",
            prodlisttag = "offers",
            prodtag = "offer"
        ):

        self.shopobj = shopobj

        self.catstag = catstag
        self.prodlisttag = prodlisttag
        self.prodtag = prodtag

        rb = xlrd.open_workbook(xlfile,formatting_info=True)
        self.sheet = rb.sheet_by_index(0)


        categories = self.colbyname("category")[1:]
        vendors = self.colbyname("vendor")[1:]
        countries = self.colbyname("country_of_origin")

        res, new_categories = self.shopobj.setCategories(categories)

        if countries:
            countries = countries[1:]

        res, new_vendors = self.shopobj.setVendors(vendors, countries)

        self.setOffers(new_categories, new_vendors)


    def setOffers(self, new_categories, new_vendors):

        rowmap = self.colmap()

        for num in range(1, self.nrows()):

            try:

                self.setProduct(new_categories, new_vendors, rowmap, num)

            except Exception, e:
                raise YMLError(e, "XL File isn't correct. Error in set products part row num="+str(num))




    def setProduct(self ,new_categories, new_vendors, rowmap, num):

        new_product =  Products()
        row = self.row(num)

        new_product.shop = self.shopobj

        new_product.category = new_categories[num-1]
        new_product.vendor = new_vendors[num-1]
        new_product.model = str(row[rowmap["model"]]).lower().strip()
        new_product.available = bool(row[rowmap["available"]])
        if rowmap.has_key("url"):
            new_product.url = row[rowmap["url"]]
        new_product.price = float(row[rowmap["price"]])
        new_product.currencyId = row[rowmap["currencyId"]]

        if rowmap.has_key("sales_notes"):
            new_product.sales_notes = row[rowmap["sales_notes"]]
        if rowmap.has_key("manufacturer_warranty"):
            new_product.manufacturer_warranty = bool(row[rowmap["manufacturer_warranty"]])
        if rowmap.has_key("barcode"):
            new_product.barcode = row[rowmap["barcode"]]
        if rowmap.has_key("description"):
            new_product.description = row[rowmap["description"]]
        if rowmap.has_key("typePrefix"):
            new_product.typePrefix = row[rowmap["typePrefix"]]
        if rowmap.has_key("local_delivery_cost") and row[rowmap["local_delivery_cost"]]:
            new_product.local_delivery_cost = int(row[rowmap["local_delivery_cost"]])
        if rowmap.has_key("delivery"):
            new_product.delivery = bool(row[rowmap["delivery"]])
        if rowmap.has_key("downloadable"):
            new_product.downloadable = bool(row[rowmap["downloadable"]])


        new_product.save()




    def xlsheet(self):
        return self.sheet
    
    def row(self, rownum):
        row = self.sheet.row_values(rownum)
        return row 
        
    def col(self, colnum):
        return self.sheet.col_values(colnum)
    
    def v(self, i, j):
        return self.sheet.cell(i,j).value
    
    def colbyname(self, name):
        
        for col_index in range(self.sheet.ncols):
            if self.sheet.cell(0, col_index).value == name:
                return self.sheet.col_values(col_index)
            
        return False
    
    def colmap(self):
        
        d = {}
        
        for col_index in range(self.sheet.ncols):
            d[self.sheet.cell(0, col_index).value] = col_index 
            
        return d
    
    def nrows(self):
        return self.sheet.nrows






class YML:


    def __init__(self, filearg, shopobj="",
                    shoptag = "shop",
                    catstag = "categories",
                    prodlisttag = "offers",
                    prodtag = "offer",
                    paramtag = "param"
                 ):

        self.path = filearg

        self.shoptag = shoptag
        self.catstag = catstag
        self.prodlisttag = prodlisttag
        self.prodtag = prodtag
        self.paramtag = paramtag

        self.shop_key = shopobj     # ShopInfo object

        self.updated_products = []
        self.new_products = []

        try:
            self.tree = etree.parse(self.path)
            self.doc = self.tree.getroot()
        except Exception, e:
            raise YMLError(e, "YML_init: Error in YML file: " + str(e) )


    def getshopdata(self):
        return self.shop_key

    def setdbdata(self):


        self.shop_elem =  self.doc.find(self.shoptag)

        if self.shop_elem is None:
            raise YMLError( "" ,"setdbdata: YML file should contain shop element ")
        self.shop_key = self.setShopInfo()

        self.cats_elem = self.shop_elem.find(self.catstag)
        self.prodlist_elem = self.shop_elem.find(self.prodlisttag)

        if self.cats_elem is None:
            raise YMLError( "" ,"setdbdata: YML file should contain "+self.catstag+" element ")

        if self.prodlist_elem is None:
            raise YMLError( "" ,"setdbdata: YML file should contain "+self.prodlisttag+" element ")

        new_categories =  self.setCategories()
        self.setOffers(new_categories)

        return True




    def setShopInfo(self):

        if self.shop_key == "":
            raise YMLError( "" ,"setShopInfo: db shop obj hasn't been defined")

        new_sh = self.shop_key

        if new_sh.name == "def":
            new_sh.name = self.shop_elem.find("name").text

        if new_sh.url == "def":
            new_sh.url = self.shop_elem.find("url").text

        agency_var = self.shop_elem.find("agency")
        if new_sh.agency == "" and agency_var is not None: new_sh.agency = agency_var.text

        company_var = self.shop_elem.find("company")
        if new_sh.company == "def" and company_var is not None: new_sh.company = company_var.text

        email_var = self.shop_elem.find("email")
        if new_sh.email == "def" and email_var is not None: new_sh.email = email_var.text

        if new_sh.name == "def" or new_sh.name is None:
            raise YMLError("",  "setShopInfo: shop name should be defined in YML file")

        if new_sh.url == "def" or new_sh.url is None:
            raise YMLError("",  "setShopInfo: shop url should be defined in YML file")

        try:
            new_sh.save()
        except Exception, e:
            raise YMLError(e,  "setShopInfo: Can't save new shop params")


        return new_sh



    def setProduct(self, parent, cat_key):

        if "id" in parent.attrib:
            parent_id = parent.get("id")
        else:
            parent_id = ""

        product_key = None

        try:
            new_product =  Products()

            new_product.shop = self.shop_key
            new_product.category = cat_key
            product_model_var = parent.find("name")
            if product_model_var is None:
                product_model_var = parent.find("model")

            if product_model_var is None or product_model_var.text is None or product_model_var.text == "":
                raise YMLError("", "setProduct: model name is empty in offer " + parent_id)

            new_product.model = product_model_var.text

            new_product.model = new_product.model.lower().strip()

            # creating Vendor
            new_vendor = Vendors()

            new_vendor.name = parent.find("vendor").text
            if new_vendor.name is None or new_product.model == "":
                raise YMLError("", "setProduct: vendor name is empty in offer " + parent_id)

            new_vendor.name = new_vendor.name.lower().strip()

            if parent.find("vendorCode") is not None:
                new_vendor.vendorCode = parent.find("vendorCode").text
            if parent.find("country_of_origin") is not None:
                new_vendor.country_of_origin = parent.find("country_of_origin").text

            # check for the same vendor
            obj = Vendors.objects.filter(
                name = new_vendor.name,
                country_of_origin = new_vendor.country_of_origin
            )
            if obj.count() > 0:
                new_product.vendor = obj[0]
                self.shop_key.vendors.add(obj[0])
            else:
                new_vendor.save()
                new_product.vendor = new_vendor
                self.shop_key.vendors.add(new_vendor)

            # check for the same product
            old_product = Products.objects.filter(shop=new_product.shop, vendor=new_product.vendor,
                category=new_product.category, model=new_product.model)

            if old_product.count() > 0:
                new_product = old_product[0]
                self.updated_products.append(new_product)
            else:
                self.new_products.append(new_product)

            new_product.available = bool(parent.get('available'))

            if parent.find("url") is not None:
                new_product.url = parent.find("url").text

            new_product.price = parent.find("price").text
            new_product.currencyId = parent.find("currencyId").text

            if new_product.price is None or new_product.price == "":
                raise YMLError("", "setProduct: price is empty in offer " + parent_id)
            if new_product.currencyId is None or new_product.currencyId == "":
                raise YMLError("", "setProduct: currencyId is empty in offer " + parent_id)

            new_product.price = float(new_product.price)

            if parent.find("sales_notes") is not None:
                new_product.sales_notes = parent.find("sales_notes").text
            if parent.find("manufacturer_warranty") is not None:
                new_product.manufacturer_warranty = bool(parent.find("manufacturer_warranty").text)
            if parent.find("barcode") is not None:
                new_product.barcode = parent.find("barcode").text
            if parent.find("description") is not None and parent.find("description").text is not None:
                new_product.description = parent.find("description").text
            if parent.find("typePrefix") is not None:
                new_product.typePrefix = parent.find("typePrefix").text
            if parent.find("local_delivery_cost") is not None:
                new_product.local_delivery_cost = int(parent.find("local_delivery_cost").text)
            if parent.find("delivery") is not None:
                new_product.delivery = bool(parent.find("delivery").text)
            if parent.find("downloadable") is not None:
                new_product.downloadable = bool(parent.find("downloadable").text)

            new_product.save()
            product_key = new_product

            self.setParams([child for child in parent if child.tag=="param"], product_key, parent_id)

        except Exception, e:
            raise YMLError(e, "setProduct: error in offer " + parent_id)






    def setParams(self, params, product_key, prod_id):

        try:
            for node in params:
                new_param = Params()
                new_param.product = product_key
                new_param.name = unicode(node.get('name'))
                new_param.data = unicode(node.text)
                new_param.data = new_param.data[:255]
                if node.get('unit') is not None:
                    new_param.unit = unicode(node.get('unit'))
                new_param.save()

        except Exception, e:
            raise YMLError(e, "Error in params:" + product_key.model + " (id="+ prod_id +")" +" : " +  new_param.name)



    def setOffers(self, new_categories):

        for node in self.prodlist_elem:

            try:
                cat_id = int(node.find("categoryId").text)
                cat = new_categories[cat_id]
            except Exception, e:
                if "id" in node.attrib:
                    raise YMLError(e, "setOffers: bad category number in offer " + str(node.get("id")) )
                else:
                    raise YMLError(e, "setOffers: bad category number in offer ")

            self.setProduct(node, cat)



    def setCategories(self):

        CatIds = {}

        # arr with categories names
        arr = [ node.text for node in self.cats_elem if node.tag == "category" ]

        if len(arr) == 0:
            raise YMLError("", "setCategories: categories list is empty")

        res, new_categories = self.shop_key.setCategories(arr)

        if res is False:
            raise  YMLError(str(arr), "ShopInfo->setCategories: failed")

        for i, node in enumerate(self.cats_elem):
            if node.tag != "category": continue

            if node.text == "" or node.text is None:
                raise YMLError("cat num: "+str(i), "setCategories: category name is empty")
            if 'id' not in node.attrib:
                raise YMLError("cat num: "+str(i), "setCategories: category "+ node.text +" doesn't have id")

            CatIds[int( node.get("id") )] = new_categories[i]


        return CatIds


                        