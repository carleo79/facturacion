from django.urls import path
from .views import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceUpdateView,
    InvoiceDeleteView,
    InvoiceLineItemListView,
    InvoiceLineItemCreateView,
    InvoiceLineItemUpdateView,
    InvoiceLineItemDeleteView,
    InvoicePaymentListView,
    InvoicePaymentCreateView,
    InvoicePaymentUpdateView,
    InvoicePaymentDeleteView,
    InvoicePrintView,
)

app_name = 'facturas'

urlpatterns = [
    path('', InvoiceListView.as_view(), name='list'),
    path('nueva/', InvoiceCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', InvoiceUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', InvoiceDeleteView.as_view(), name='delete'),
    path('<int:pk>/imprimir/', InvoicePrintView.as_view(), name='print'),
    # Items
    path('<int:invoice_id>/items/', InvoiceLineItemListView.as_view(), name='items_list'),
    path('<int:invoice_id>/items/nuevo/', InvoiceLineItemCreateView.as_view(), name='items_create'),
    path('<int:invoice_id>/items/<int:pk>/editar/', InvoiceLineItemUpdateView.as_view(), name='items_update'),
    path('<int:invoice_id>/items/<int:pk>/eliminar/', InvoiceLineItemDeleteView.as_view(), name='items_delete'),
    # Pagos
    path('<int:invoice_id>/pagos/', InvoicePaymentListView.as_view(), name='payments_list'),
    path('<int:invoice_id>/pagos/nuevo/', InvoicePaymentCreateView.as_view(), name='payments_create'),
    path('<int:invoice_id>/pagos/<int:pk>/editar/', InvoicePaymentUpdateView.as_view(), name='payments_update'),
    path('<int:invoice_id>/pagos/<int:pk>/eliminar/', InvoicePaymentDeleteView.as_view(), name='payments_delete'),
]


