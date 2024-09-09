import json 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, Producto, Carrito, ItemCarrito, Cupon, HistorialCompras, Categoria, CustomUser, Boleta
from .forms import RegistroForm, ProfileForm, ProductoForm
from django.db import models
from django.db import models
from django.conf import settings


def index(request, categoria_nombre=None):
    if categoria_nombre:
        categoria = get_object_or_404(Categoria, nombre=categoria_nombre)
        productos = Producto.objects.filter(categoria=categoria)
    else:
        productos = Producto.objects.all()
    
    context = {
        'productos': productos,
        'categoria': categoria if categoria_nombre else None
    }
    return render(request, 'tienda/base.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            login(request, user)
            messages.success(request, 'Tu cuenta ha sido creada exitosamente.')
            return redirect('index')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'tienda/login/registro.html', {'form': form})

def login_view(request):
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username:
            messages.error(request, "Por favor, ingrese su nombre de usuario.")
        if not password:
            messages.error(request, "Por favor, ingrese su contraseña.")

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                if not CustomUser.objects.filter(username=username).exists():
                    messages.error(request, "Usuario no encontrado.")
                else:
                    messages.error(request, "Contraseña incorrecta.")
    
    return render(request, 'tienda/login/login.html', {'username': username})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'tienda/carrito/carrito.html', {'items': items, 'total': total})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.unidades < 1:
        messages.error(request, "Este producto no está disponible en stock.")
        return redirect('detalle_producto', id=producto.id)

    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item, item_created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not item_created:
        if item.cantidad < producto.unidades:
            item.cantidad += 1
            item.save()
        else:
            messages.error(request, "No hay suficientes unidades disponibles.")
    else:
        item.save()
    
    return redirect('carrito')

@login_required
def eliminar_item(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = get_object_or_404(Carrito, usuario=request.user)
    item = get_object_or_404(ItemCarrito, carrito=carrito, producto=producto)
    item.delete()
    return redirect('carrito')

@login_required
def actualizar_cantidad(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = get_object_or_404(Carrito, usuario=request.user)
    item = get_object_or_404(ItemCarrito, carrito=carrito, producto=producto)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
        else:
            item.delete()
    return redirect('carrito')


@login_required
def aplicar_cupon(request):
    if request.method == 'POST':
        codigo = request.POST.get('cupon', '').strip()  # Capturar el código y eliminar espacios en blanco
        carrito = get_object_or_404(Carrito, usuario=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
        total = sum(item.producto.precio * item.cantidad for item in items)
        cupon_error = None
        total_con_descuento = total

        if not codigo:  # Verificar si el código del cupón está vacío
            cupon_error = "Por favor, ingrese un código de cupón."
            messages.error(request, cupon_error)
        else:
            try:
                cupon = Cupon.objects.get(codigo=codigo, activo=True, fecha_expiracion__gte=timezone.now())
                total_con_descuento = total * (1 - cupon.descuento / 100)
                messages.success(request, f"Cupón aplicado. Descuento: {cupon.descuento}%.")
            except Cupon.DoesNotExist:
                cupon_error = "El cupón no es válido o ha expirado."
                messages.error(request, cupon_error)

        # Renderizar o redireccionar de acuerdo a si el cupón fue aplicado o no
        return render(request, 'tienda/carrito/carrito.html', {
            'items': items,
            'total': total_con_descuento,
            'cupon_error': cupon_error
        })

    return redirect('carrito')


@login_required
def checkout(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    
    if not items:
        messages.error(request, "No hay productos en el carrito.")
        return redirect('carrito')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,  # Aquí cambiamos `username` por `user`
            direccion=request.POST.get('direccion'),
            telefono=request.POST.get('telefono'),
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            email=request.POST.get('email'),
            total_pagado=sum(item.producto.precio * item.cantidad for item in items),
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                producto=item.producto,
                cantidad=item.cantidad,
                total=item.producto.precio * item.cantidad,
            )
            item.producto.unidades -= item.cantidad
            item.producto.save()

        items.delete()  # Limpiar el carrito después de realizar la orden
        return redirect('orden_confirmacion', order_id=order.id)

    return render(request, 'tienda/carrito/checkout.html', {'items': items})


@login_required
def boleta(request, boleta_id):
    boleta = get_object_or_404(Boleta, id=boleta_id, usuario=request.user)
    return render(request, 'tienda/carrito/boleta.html', {'boleta': boleta})

@login_required
def profile_view(request):
    return render(request, 'tienda/usuario/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('profile')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'tienda/usuario/edit_profile.html', {'form': form})

@login_required
def favorites_view(request):
    favorites = request.user.favorite_items.all()
    return render(request, 'tienda/usuario/favorites.html', {'favorites': favorites})

@login_required
def panel_control(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/admin/panel_control.html', {'productos': productos})

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.admin = request.user
            producto.save()
            return redirect('panel_control')
    else:
        form = ProductoForm()
    return render(request, 'tienda/admin/agregar_producto.html', {'form': form})

@login_required
def eliminar_producto(request, producto_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para eliminar productos.")
        return redirect('panel_control')

    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('panel_control')

@login_required
def historial_compras(request):
    compras = HistorialCompras.objects.filter(usuario=request.user)
    return render(request, 'tienda/adminn/historial_compras.html', {'compras': compras})

@login_required
def filtrar_productos_por_categoria(request, categoria_nombre):
    categoria = get_object_or_404(Categoria, nombre=categoria_nombre)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'tienda/productos_categoria.html', {'productos': productos, 'categoria': categoria})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

@login_required
def orden_confirmacion(request, order_id):
    orden = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'tienda/carrito/orden_confirmacion.html', {'orden': orden})


