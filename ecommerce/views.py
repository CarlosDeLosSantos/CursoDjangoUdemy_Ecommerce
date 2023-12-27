from django.shortcuts import render
from store.models import Product

def home(request): #Metodo que solicita un render del html home.
    
    products = Product.objects.all().filter(is_avaliable=True)
    
    context = {
        'products': products,
    }
    
    
    return render(request, 'home.html',context)