from django.contrib import admin
from .models import Cart, CartItem


# Register your models here.
#Siempre que se registren nuevos modelos es necesario realizar las migraciones
admin.site.register(Cart)
admin.site.register(CartItem)