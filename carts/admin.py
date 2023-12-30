from django.contrib import admin
from .models import Cart, CartItem


# Register your models here.

#CartAdmin es para mostrar el modelo con el id y la fecha de creación del carrito en la página de admin
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
    
#CartItemAdmin permite mostrar el producto, el id del carrito, al cantidad y si está activo en el carrito en cuestión dentro
#del admin de Django    
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')

#Siempre que se registren nuevos modelos es necesario realizar las migraciones
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)