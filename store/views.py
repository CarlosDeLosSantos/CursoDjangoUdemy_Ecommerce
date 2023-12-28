from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
# Create your views here.
def store(request, category_slug=None):
    #PAra filtrar por categorias
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_avaliable = True).order_by('id')
        paginator = Paginator(products, 3)
        #Capturando el valor de la página desde la url ()
        page = request.GET.get('page')
        #Indicando que envíe la lista de páginas (que envíe los productos que están en la página en cuestión)
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_avaliable = True).order_by('id')
        #Para obtener pagincacion (Solo mostrar cierta cantidad de productos por página)
        paginator = Paginator(products, 3)
        #Capturando el valor de la página desde la url ()
        page = request.GET.get('page')
        #Indicando que envíe la lista de páginas (que envíe los productos que están en la página en cuestión)
        paged_products = paginator.get_page(page)
        product_count = products.count()

    
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        #Checar linea comentada para mejor funcionamiento: Validar slug de producto y Slug de categoria
        #single_product = Product.objects.get(category__slug==category_slug, slug=product_slug)
        single_product = Product.objects.get(slug=product_slug)
        #Checar si el producto ya está en el carrito
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
    except Exception as e:
        raise e
    #Diccionario para almacenar las variables y objetos consultados anteriormente
    context={
        'single_product': single_product,
        'in_cart': in_cart,
    }
    
    return render(request, 'store/product_detail.html', context)

#Método para búsqueda específica de un producto (Barra de búsqueda)
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        #Comparando la búsqueda ingresada por el usuario con los datos guardados edel producto (descripción o nombre del producto)
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=products.count()
            
    #Diciconario para almacenar las variables consultadas
    context = {
        'products':products,
        'product_count':product_count,
    }
    
    return render(request, 'store/store.html', context)