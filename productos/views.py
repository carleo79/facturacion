from django.http import JsonResponse, Http404
from .models import ProductPresentation


def product_presentation_detail(request, pk: int):
    try:
        p = ProductPresentation.objects.select_related('product').get(pk=pk)
    except ProductPresentation.DoesNotExist:
        raise Http404
    data = {
        'id': p.id,
        'sku': p.sku or '',
        'name': p.name,
        'product_name': p.product.name,
        'unit_price': str(p.base_price or 0),
        'unit_of_measure': p.unit_of_measure,
    }
    return JsonResponse(data)

# Create your views here.
