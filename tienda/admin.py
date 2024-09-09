from django.contrib import admin
from .models import CustomUser, Producto, Carrito, ItemCarrito, Cupon, Boleta, HistorialCompras, Categoria

# Registro de modelos sin configuraciones adicionales
admin.site.register(CustomUser)
admin.site.register(Cupon)
admin.site.register(Categoria)

# Configuración del modelo Producto con una clase ModelAdmin personalizada
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'unidades', 'seccion', 'categoria', 'es_oferta', 'genero', 'admin']
    list_filter = ['seccion', 'categoria', 'genero', 'es_oferta']
    search_fields = ['nombre']

    # Personalizando el formulario
    def formfield_for_dbfield(self, db_field, **kwargs):
        if (db_field.name == 'unidades_por_talla'):
            kwargs['widget'] = admin.widgets.AdminTextareaWidget(attrs={'placeholder': 'Ejemplo: {"L": 15, "M": 10, "S": 5}'})
        return super().formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Producto, ProductoAdmin)

# Configuración del modelo HistorialCompras con una clase ModelAdmin personalizada
class HistorialComprasAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'fecha_compra')
    search_fields = ('usuario__username', 'producto__nombre')

admin.site.register(HistorialCompras, HistorialComprasAdmin)

# Configuración del modelo Boleta con una clase ModelAdmin personalizada
class BoletaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'total')
    search_fields = ('usuario__username',)

admin.site.register(Boleta, BoletaAdmin)

# Registro de los demás modelos sin configuraciones adicionales
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
