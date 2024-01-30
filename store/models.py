from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_avaliable = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
   
   #Método para obtener url y poder mostrar la ágina dinámica del producto 
   #Lo toma directamente del archivo urls.py
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    #Método para obtener y mostrar en el home el nombre del producto
    def __str__(self):
        return self.product_name
    
    #Obtener Promedio de puntuaciones
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg=0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
            return avg
        
    #Contador de Comentarios
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    
    
#Clase para diferenciar entre variaciones (Diferenciar variaciones de tallas, colores, etc)
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color', is_active=True)
    def tallas(self):
        return super(VariationManager,self).filter(variation_category='talla', is_active=True)
    

#Diccionario para el elemento Choices de Clase Variation
variation_category_choice=(
    ('color', 'color'),
    ('talla', 'talla'),
)
#Clase para las variaciones de productos(Tallas, colores, etc)
class Variation(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    #Instanciando VariationManager para podr utilizar sus métodos
    objects = VariationManager()
    
    #__str__ retorna unicamente el nombre del objeto, ya que se está transformando a string
    # def __str__(self):
    #     return str(self.product)
    
    #__unicode__ retorna el objeto de tipo objeto. Se debe realizar la respectiva variacion en admin.py para que muetsre todos los
    #datos del objeto en cuestión y no solo un variationobject
    # def __unicode__(self):
    #     return self.product
    
    
    #Realizando otro __str__ para que retorne de manera más legible las variations en Admin
    def __str__(self):
        return self.variation_category + ':' + self.variation_value
    
    
    
#No olvidar registar los modelso en Admin.py

#Entidad para calificaciones de productos.

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject