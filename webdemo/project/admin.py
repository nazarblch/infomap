from django.contrib import admin
from project.models import Keyword


class KeywordsAdmin(admin.ModelAdmin):
    #list_display_links = ('product',)
    list_filter = ('product__shop', 'product','pattern')

admin.site.register(Keyword, KeywordsAdmin)
