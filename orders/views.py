from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.

#Para los pagos
#guarda en la BD lso datos mandados desde el Script tipo Js que conecta a paypal con el payments.html
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_id = order.order_total,
        status = body['status'],
        
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    
    #Par amover todos los productos del carrito a la tabla order product
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id    
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        
        orderproduct.save()
        
        #PAra mostrar variations en Productos dentro de Orden
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        
        orderproduct.save()
        
        #PAra Actualizar el carrito y el stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        
        product.save()
        
    CartItem.objects.filter(user=request.user).delete()
    
    ##Para enviar Email con orden de compra
    mail_subject = 'Gracias Por tu Compra'
    body = render_to_string('orders/order_received_email.html', {
        'user' : request.user,
        'order' : order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, body, to=[to_email])
    
    send_email.send()
    
    #Para redireccionar a la página d eorden de compra
    
    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }
    
    
    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        
    tax = (2 * total)/100
    grand_total = total + tax
    
    #PAra agregar a la orden de compra los datos del cliente
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.addres_line_1 = form.cleaned_data['addres_line_1']
            data.addres_line_2 = form.cleaned_data['addres_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city= form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            #PAra fecha de creación de orden
            
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr, mt, dt)
             # Fecha en formato: 20280110
            current_date = d.strftime("%Y%m%d")
            
            #Concatenado id para crear un numero de orden unico
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            #Obteniendo la orden para redireccionar al payment
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
            }
            
            return render(request, 'orders/payments.html', context)
        
    else:
        return redirect('checkout')
           
#PAra la página de confirmación de orden
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        
        for i in ordered_products:
            subtotal += i.product_price*i.quantity
            
        payment = Payment.objects.get(payment_id=transID)
        
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
        }
    
        return render(request, 'orders/order_complete.html', context)
    
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
        
