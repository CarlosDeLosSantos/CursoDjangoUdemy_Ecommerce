from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
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
    
    #Para añadir Variations al carrito
    #1 Se crea un arreglo para guardar las variations
    product_variation = []
    #2 Se verifica que se esté utilizando el método Post
    #Si si es POST, se capturaran todas las variations enviadas con un bucle
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
    #3 Se verifica si el variation está en la colección, dentro de la BD
    #De esa forma se crea un obojetom Varitaion
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
    #4 Se añade al arreglo creado anteriormente
                product_variation.append(variation)
            except:
                pass
            
    
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
    
    #Verificar si ya existe el CartItem con ciertas variations
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    
    
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        #Insertando cada variation al CartItem en caso de que ya exista con la misma variation
        #Solo se ejecuta si product_variation no está vacía
        
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id) 
            
        #Si ya existe el item con las Variations, solo insertara un elemento a la misma linea del item en el carrito
        #No creara una nueva línea en el carrito
        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item=CartItem.objects.get(product=product, id=item_id)
            item.quantity +=1
            item.save()
            
        #En caso de que noe xista el Item con las variations ni en el carrito, ni en la BD
        #Creará un nuevo CartItem
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart )
        if len(product_variation)>0:
            item.variations.clear()
            item.variations.add(*product_variation)
            
        item.save()
        
    #El siguiente else se lanza cuando es la primera vez añadiendo un producto al carito.
    else:
        cart_item = CartItem.objects.create(
           product = product,
           quantity = 1,
           cart = cart, 
        )
        #Se utiliza el mismo if para el except, apra tambien agregar las variations al CartItem 
        #generado desde cero
        if len(product_variation)>0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
        
    return redirect('cart')


#Quita Productos del carrito   
def remove_cart(request, product_id, cart_item_id):
    #Para encontrar el objeto Cart en cuestión
    cart = Cart.objects.get(cart_id=_cart_id(request))  
    #Para encontrar el objeto Product en cuestión   
    product = get_object_or_404(Product, id=product_id)
    #Para encontarr el producto y el carrito que queremos eliminar (La instancia)
    
    try:  
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
        #Si el cart_item es > 1, se decrementa. Cualquier otro caso (que sea 0), se elimina.
        if cart_item.quantity>1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
        
    return redirect('cart')
    #Para retornar una respuesta http en vez de None
    #No olvidar registrar el path que invoca este método en urls.py
    
#Borrar Producto del cart
def remove_cart_item(request, product_id, cart_item_id):
    #Para encontrar el objeto Cart en cuestión
    cart = Cart.objects.get(cart_id=_cart_id(request))  
    #Para encontrar el objeto Product en cuestión   
    product = get_object_or_404(Product, id=product_id)
    #Para encontarr el producto y el carrito que queremos eliminar (La instancia)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    #Eliminar el item del carrtio
    cart_item.delete()
    
    return redirect('cart')
    #Para retornar una respuesta http en vez de None
    
    
    
    

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
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
