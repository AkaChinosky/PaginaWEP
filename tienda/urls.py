from django.urls import path
from . import views  # Solo necesitas esta línea
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('categoria/<str:categoria_nombre>/', views.index, name='productos_por_categoria'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('admin/panel/', views.panel_control, name='panel_control'),
    path('admin/agregar/', views.agregar_producto, name='agregar_producto'),
    path('admin/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('admin/historial/', views.historial_compras, name='historial_compras'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_item, name='eliminar_item'),
    path('carrito/checkout/', views.checkout, name='checkout'),
    path('actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('aplicar_cupon/', views.aplicar_cupon, name='aplicar_cupon'),
    path('boleta/<int:boleta_id>/', views.boleta, name='boleta'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('orden/confirmacion/<int:order_id>/', views.orden_confirmacion, name='orden_confirmacion'),
]

# Añade la configuración para servir archivos de media solo si DEBUG está activado
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)