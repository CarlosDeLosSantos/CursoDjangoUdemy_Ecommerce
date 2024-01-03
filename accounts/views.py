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
            auth.login(request, user)
            return redirect('home')
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