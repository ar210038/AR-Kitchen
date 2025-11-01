from .models import Flavor

def global_context(request):
    return {
        'flavors': Flavor.objects.all()
    }