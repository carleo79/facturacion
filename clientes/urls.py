from django.urls import path
from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    clientes_search,
)

app_name = 'clientes'

urlpatterns = [
    path('', ClienteListView.as_view(), name='list'),
    path('nuevo/', ClienteCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', ClienteUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='delete'),
    path('api/buscar/', clientes_search, name='api_buscar'),
]


