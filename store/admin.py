from django.contrib import admin
from .models import Product, Variation
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_avaliable')
    prepopulated_fields = {'slug': ('product_name',)}
    
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)

#Los modelos y clases admin.ModelAdmin son como se mostrarán idealmente en el administrador de Django

#No olvidar realizar proceso de Migrationpara registrar en DB
    #python manage.py makemigrations
    #python manage.py migrate

