from django import forms 
from .models import ReviewRating

#Formulario hecho con Python que se mostrará después en el HTML

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']