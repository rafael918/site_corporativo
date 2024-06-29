from django.urls import path
from views import perfil_view

urlpatterns = [
    path('<slug:username>/', perfil_view, name='perfil'),
]