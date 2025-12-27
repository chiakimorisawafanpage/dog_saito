from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Exists, OuterRef
from .models import Product, Category, Size

def index(request):
    try:
        new_arrivals_category = Category.objects.get(slug='new-arrivals')
        products = Product.objects.filter(
            available=True, 
            categories=new_arrivals_category
        ).prefetch_related('images').distinct()[:50]
    except Category.DoesNotExist:
        products = Product.objects.filter(available=True).prefetch_related('images')[:10]
        
    return render(request, 'products/index.html', {'products': products})

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        categories_to_filter = category.children.all() | Category.objects.filter(id=category.id)
        products = products.filter(categories__in=categories_to_filter).distinct()

    available_sizes = Size.objects.filter(product__in=products).values_list('name', flat=True).distinct()
    
    def size_sort_key(s):
        order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']
        if s.upper() in order:
            return (0, order.index(s.upper()))
        try:
            return (1, float(s))
        except ValueError:
            return (2, s)
            
    available_sizes = sorted(list(available_sizes), key=size_sort_key)

    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(sizes__name__in=selected_sizes).distinct()

    sort_by = request.GET.get('sort')
    
    new_arrival_subquery = Product.categories.through.objects.filter(
        product_id=OuterRef('pk'),
        category__slug='new-arrivals'
    )
    products = products.annotate(is_new_arrival=Exists(new_arrival_subquery))

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-is_new_arrival', '-created')
    
    products = products.prefetch_related('categories')
        
    return render(request, 'products/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'available_sizes': available_sizes,
        'selected_sizes': selected_sizes,
        'sort_by': sort_by,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    related_products = Product.objects.filter(available=True, categories__in=product.categories.all()).exclude(id=product.id).distinct()[:4]
    
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products
    })
