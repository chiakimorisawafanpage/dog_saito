from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['email', 'first_name', 'last_name', 'address', 'city', 'postal_code']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Фамилия'}),
            'address': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Адрес'}),
            'city': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Город'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': 'Индекс'}),
        }

