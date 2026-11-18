from .models import Material

def menu_links(request):
    links = Material.objects.all()
    return dict(links=links)