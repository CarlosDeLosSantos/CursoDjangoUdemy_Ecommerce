from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request): #Metodo que solicita un render del html home.
    
    products = Product.objects.all().filter(is_avaliable=True).order_by('created_date')
    
    #Para obtener las calificaciones de los producto
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    
    context = {
        'products': products,
        'reviews': reviews,
    }
    
    
    return render(request, 'home.html',context)