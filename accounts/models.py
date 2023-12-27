from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

#Modelo para un superAdmin

class MyAccountManager(BaseUserManager):
    #Método que permite crear un nuevo usuario dentro de la app
    def create_user(self, username, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('El usuario debe tener Email')
        if not username:
            raise ValueError('El usuario debe tener un username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    #Método para crear un super usuario
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            
        )
        
        #Escribiendo atributos extra que debe tener un admin
        
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superAdmin = True
        user.save(using=self._db)
        return user



#Modelo Abstracto para la clase Account
#Recordar configurar el modelo Account como el modelo principal para Django.
#Para ello se modifica el settings.py de ecommerce
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    
    #Definiendo campos atributo de Django
    #Necesario Declararlos para evitar errores
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    
    #Definiendo el inicio de sesión con Email en vez de User name de Django
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name'] #Para Indicar que datos son requeridos al regfistrar usuario
    
    #Para incluir los métodos de MyAccountManager dentro del modelo Account
    objects = MyAccountManager()
    
    #Para definir que el email es con el que lista al usuario
    def __str__(self):
        return self.email
    
    #Para indicar si el usuario tiene permisos de administrador.
    #Solo retorna siu is_admin=true
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    #Para indicar si tiene acceso a los modulos
    def has_module_perms(self, add_label):
        return True
    
    #Como se han realizado modificaciones directas sobre el Framework, no olvidar borrar los registros realizados con anterioridad en archivo db.sqlite3
    #Tambien, eliminar las migraciones realizadas con anterioridad