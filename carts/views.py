from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

#Métodos para crear carrito de compras

#Obtiene el cart id tomando en cuenta la sesion del usuario
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart =request.session.create()
    return cart
#Añade al carrito en caso de existir. Si no existe un carrito, cra uno nuevo.
def add_cart(request, product_id):
    #Buscar Producto mediante el id
    product = Product.objects.get(id = product_id)
    
    #Crear Carrito en caso de no existir
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        
    cart.save()
    
    #Insertando el producto
    #Busca por producto y por carrito de compras
    #El seiguiente try es en caso de que ya se encuentre el objeto dentro del carrito
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    #El siguiente Except se lanza cuando es la primera vez añadiendo un producto al carito.
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
           product = product,
           quantity = 1,
           cart = cart, 
        )
        
        cart_item.save()
    return redirect('cart')


#Quita Productos del carrito   
def remove_cart(request, product_id):
    #Para encontrar el objeto Cart en cuestión
    cart = Cart.objects.get(cart_id=_cart_id(request))  
    #Para encontrar el objeto Product en cuestión   
    product = get_object_or_404(Product, id=product_id)
    #Para encontarr el producto y el carrito que queremos eliminar (La instancia)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    #Si el cart_item es > 1, se decrementa. Cualquier otro caso (que sea 0), se elimina.
    if cart_item.quantity>1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
        
    return redirect('cart')
    #Para retornar una respuesta http en vez de None
    #No olvidar registrar el path que invoca este método en urls.py
    
#Borrar Producto del cart
def remove_cart_item(request, product_id):
    #Para encontrar el objeto Cart en cuestión
    cart = Cart.objects.get(cart_id=_cart_id(request))  
    #Para encontrar el objeto Product en cuestión   
    product = get_object_or_404(Product, id=product_id)
    #Para encontarr el producto y el carrito que queremos eliminar (La instancia)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    #Eliminar el item del carrtio
    cart_item.delete()
    
    return redirect('cart')
    #Para retornar una respuesta http en vez de None
    
    
    
    

def cart(request, total=0, quantity=0, cart_items=None):
    #Consultar si existe el elemento en la BD
    try:
        cart = Cart.objects.get(cart_id= _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        #Bucle for para saber precio total y cantitdad total de productos en carrito
        for cart_item in cart_items:
            total+= (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        #Para mostrar el total en el carrito
        tax = (2*total)/100
        grand_total = total+tax    
        
    except ObjectDoesNotExist:
        pass #Ignora la excepcion
    #Diciconario donde se guardaran los elementos declarados anteriormente para mostrarlos en el render.    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':grand_total,
    }
    
    return render(request, 'store/cart.html', context)
