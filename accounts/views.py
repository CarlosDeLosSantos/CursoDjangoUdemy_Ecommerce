from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage


from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# Create your views here.

def register(request):
    #Capturando datos que envía el cliente
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            #Añadiendo Username tomando como base el email
            #El método split parte en un arreglo el email, separado por el @
            #Tomando el método en la ubicaicón [0] tomará solo la primera parte
            #Ejemplo: caraledso@gmail.com -> [caraledso][gmail.com]
            username = email.split("@")[0]
            #Instancia un user, necesitando el método create_ser los parámetros en naranja y lso nombres de las variables en blanco
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            #Dado que create_user no tiene como parámetro phone_number, se instancia a parte
            user.phone_number = phone_number
            #Inserta el user en BD
            user.save()
            
            
            #Para Activacion de Cuenta vía Email
            
            current_site = get_current_site(request)
            mail_subject = 'Activación de Cuenta Vaxi Drez'
            body = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
            
            #Mensaje de succes
            #messages.success(request, 'Se Registró El Usuario Correctamente')
            return redirect('/accounts/login/?command=verification&email='+email)

    
    #El diccionario context es para guardar los objetos de tipo form
    context = {
        'form': form
        
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            
            #Segmento para comprobar elementos en un carrito antes de iniciar sesión
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                    cart_item= CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                        #Realiza la comparación entre los arreglos creados para un carrito sin iniciar sesión
                        #y el carrito con sesión iniciada
                        #Esto apra añadir tal elemento a las mismas variaciones registradas en el carrito
                        #O bien, crear una nueva ínea por ser una variación distinta
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            
            #############################
            
            auth.login(request, user)
            messages.success(request, 'Sesión iniciada Exitosamente')
            #http://localhost:8000/accounts/login/?next=/cart/checkout/
            #Para mandar al usuario al checkout en vez del dashboard (Cuando añada productos al carrito sin iniciar sesión)
            url = request.META.get('HTTP_REFERER')
            #PAra podr capturar el parámetro del url
            #next=/cart/checkout/
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
                
        else:
            messages.error(request,'Las credenciales son incorrectas')
            return redirect('login')
        
            


    
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    
    auth.logout(request)
    messages.success(request, 'Sesión Cerrada Exitosamente')
    
    
    
    return redirect('login')

#Activación de Cuenta vía eMail
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, tu cuenta ha sido activada')
        return redirect('login')
    else:
        messages.error(request, 'La activación es inválida')
        return redirect('register')
    
#Para el Dashboard
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

#PAra recuperar contraseña
def forgotPassword(request):
    #Comprobando que sea método POST y obteniendo el usuario desde la base de datos
    #Tomando como búsqueda el email ingresado
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Resetear Password'
            body = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
            
            messages.success(request, 'Un email fue enviadom a tu bandeja de entrada para resetear tu password')
            return redirect('login')
        else:
            messages.error(request, 'La cuenta de usuario no existe')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

#PAra validar el reset de password
def resetpassword_validate(request, uidb64, token):
    #Try para decodificar el uidb64
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    #Comprobar que el Token y usuario son correctos 
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'El Link Ha Expirado')
        return redirect('login')
    
#Resetear Password una vez cumplido lo anmterior

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'El password se reseteo correctamente')
            return redirect('login')
        else:
            messages.error(request, 'El Password de confirmación no concuerda')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
        

    
        
