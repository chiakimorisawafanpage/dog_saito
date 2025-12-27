from django import template
from products.models import Category

register = template.Library()

@register.simple_tag
def get_main_category_url(product):
    categories = product.categories.all()
    
    categories = [c for c in categories if c.slug != 'new-arrivals']
    
    target_category = None
    
    for cat in categories:
        if cat.parent:
            target_category = cat
            break
            
    if target_category:
        from django.urls import reverse
        return reverse('products:product_list_by_category', args=[target_category.slug])
        
    if categories:
        from django.urls import reverse
        return reverse('products:product_list_by_category', args=[categories[0].slug])
        
    from django.urls import reverse
    return reverse('products:product_detail', args=[product.slug])


