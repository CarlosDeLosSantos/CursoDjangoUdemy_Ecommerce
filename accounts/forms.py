from django import forms
from .models import Account

#Creando modelo del formulario de registro
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Password',
        'class':'form-control'
        
    }))
    confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={
        'placeholder': 'Confirmar Password',
        'class': 'form-control'
        
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
    #Método para aplicar clases y estilos css a los formularios generados
    #desde Django
    
    #Tambien se puede aplicar de manera individual, cómo se declaro en la seción
    #de Password en class RegistrationForm. Pero es más tedioso
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Ingrese nombre'
        self.fields['last_name'].widget.attrs['placeholder']='Ingrese apellidos'
        self.fields['phone_number'].widget.attrs['placeholder']='Ingrese teléfono'
        self.fields['email'].widget.attrs['placeholder']='Ingrese email'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
            
            
            
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                'El Password No Coincide'
            )