from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
import re
from django import forms
from .models import Producto
from django import forms
from .models import Cupon


class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'rut')

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Este campo es obligatorio.")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("El correo electrónico ya está registrado.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not re.match(r'^\d{7,8}-[0-9Kk]$', rut):
            raise forms.ValidationError("Formato de RUT inválido. Ejemplo correcto: 12345678-9")
        if CustomUser.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'telefono', 'genero', 'rut']
        widgets = {
            'genero': forms.Select(choices=[('H', 'Hombre'), ('M', 'Mujer')]),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ejemplo: +56912345678'}),
        }
        
        
        
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'foto', 'unidades', 'unidades_por_talla', 'seccion', 'es_oferta', 'genero']
        widgets = {
            'unidades_por_talla': forms.Textarea(attrs={'placeholder': 'Ejemplo: {"S": 10, "M": 5, "L": 3}'}),
        }
        
class CuponForm(forms.ModelForm):
    class Meta:
        model = Cupon
        fields = ['codigo']