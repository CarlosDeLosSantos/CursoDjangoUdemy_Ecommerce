from django.db import models
from django.urls import reverse
# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255, blank = True) 
    slug = models.CharField(max_length = 100, unique = True)
    cat_image = models.ImageField(upload_to = 'photos/categories', blank = True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
    def get_url(self):
        return reverse('products_by_category', args=[(self.slug)])
        
    
    def __str__(self):
    
        return self.category_name
    
    #str regresa el nombre de la categoria otorgado en seccion Add Category
    
    #No olvidar registrar la presente categoría en el admin de django.
    #De igual manera, no olvidar instalar el paquete pillow en el env (Para manejo de archivos)
    #Posteriormente, realizar las migraciones en python, para poder crear las entidades en el admin de django
    
    