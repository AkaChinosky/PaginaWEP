from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    SECCION_CHOICES = [
        ('Hombres', 'Hombres'),
        ('Mujeres', 'Mujeres'),
        ('Accesorios', 'Accesorios'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    foto = models.ImageField(upload_to="productos", null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.PositiveIntegerField()
    unidades_por_talla = models.JSONField()  # Para manejar unidades por tallas
    seccion = models.CharField(max_length=20, choices=SECCION_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    es_oferta = models.BooleanField(default=False)
    genero = models.CharField(max_length=20, choices=[('Hombre', 'Hombre'), ('Mujer', 'Mujer')])
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class HistorialCompras(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.cantidad})"

class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    productos = models.ManyToManyField('Producto', through='ItemCarrito')

class ItemCarrito(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_expiracion = models.DateTimeField()
    activo = models.BooleanField(default=True)

class Boleta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    detalles = models.TextField()

    def __str__(self):
        return f'Boleta {self.id} - {self.usuario.username}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField()
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} in order {self.order.id}"

class CustomUser(AbstractUser):
    genero = models.CharField(max_length=10, choices=[('H', 'Hombre'), ('M', 'Mujer')])
    telefono = models.CharField(max_length=15, blank=True, null=True)
    apellido = models.CharField(max_length=50, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True)
    favorite_items = models.ManyToManyField(Producto, related_name='favorited_by')
    
class Compra(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Completado', 'Completado')])
    fecha_compra = models.DateTimeField(auto_now_add=True)
    talla = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} - {self.fecha_compra}"
    
    
class ActividadUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha}"
