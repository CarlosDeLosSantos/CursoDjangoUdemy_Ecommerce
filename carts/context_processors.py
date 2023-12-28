from .models import Cart, CartItem
from .views import _cart_id

#Contador de objetos en carrito
def counter(request):
    cart_count=0
    try:
        #Para buscar el carrito.
        #Para filtrar el objeto Cart en cuestión
        cart = Cart.objects.filter(cart_id=_cart_id(request))  
        #Para filtrar los elementos del carrito de compras
        #Como porm defecto trae un arreglo, se especifica que traiga solo un elemento (La busqueda hecha inicialmente en la linea anterior)
        cart_items = CartItem.objects.all().filter(cart=cart[:1])
    
        #PAra saber la cantitad total de productos en el carrito
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    #¡que pasa si ocurre un error en las búquedas de cart item y cart        
    except Cart.DoesNotExist:
        cart_count=0
    
    #El return es otra manera de utiliar el clásico diccionario context usado anteriormente    
    return dict(cart_count=cart_count)
        