from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages

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
            #Mensaje de succes
            messages.success(request, 'Se Registró El Usuario Correctamente')
            return redirect('register')
            
    
    #El diccionario context es para guardar los objetos de tipo form
    context = {
        'form': form
        
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    return render(request, 'accounts/login.html')

def logout(request):
    return