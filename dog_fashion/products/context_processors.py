from .models import Category

def menu_categories(request):
    categories = Category.objects.filter(parent=None).exclude(slug__in=['clothes', 'new-arrivals']).prefetch_related('children')
    
    return {
        'menu_categories': categories
    }

