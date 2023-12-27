from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
# Create your views here.
def store(request, category_slug=None):
    #PAra filtrar por categorias
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_avaliable = True)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_avaliable = True)
        product_count = products.count()

    
    context = {
        'products': products,
        'product_count': product_count,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        #Checar linea comentada para mejor funcionamiento: Validar slug de producto y Slug de categoria
        #single_product = Product.objects.get(category__slug==category_slug, slug=product_slug)
        single_product = Product.objects.get(slug=product_slug)
    except Exception as e:
        raise e
    
    context={
        'single_product': single_product,
    }
    
    return render(request, 'store/product_detail.html', context)