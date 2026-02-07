from django.urls import path
from .views import product_presentation_detail

app_name = 'productos'

urlpatterns = [
    path('api/presentaciones/<int:pk>/', product_presentation_detail, name='presentation_detail'),
]


