from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Cliente
from django.http import JsonResponse
from django.db.models import Q


class ClienteListView(ListView):
    model = Cliente
    paginate_by = 20


class ClienteCreateView(CreateView):
    model = Cliente
    fields = [
        'codigo', 'nombre', 'tipo', 'ruc_dni', 'direccion', 'telefono', 'email',
        'limite_credito', 'estado',
    ]
    success_url = reverse_lazy('clientes:list')


class ClienteUpdateView(UpdateView):
    model = Cliente
    fields = [
        'codigo', 'nombre', 'tipo', 'ruc_dni', 'direccion', 'telefono', 'email',
        'limite_credito', 'estado',
    ]
    success_url = reverse_lazy('clientes:list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    success_url = reverse_lazy('clientes:list')


def clientes_search(request):
    q = request.GET.get('q', '').strip()
    qs = Cliente.objects.all()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(ruc_dni__icontains=q))
    results = [
        {
            'id': c.id,
            'text': f"{c.codigo} - {c.nombre}",
        }
        for c in qs.order_by('nombre')[:20]
    ]
    return JsonResponse({'results': results})

# Create your views here.
