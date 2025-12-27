from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from products.models import Product, Size
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    size_name = request.POST.get('size', None)
    
    if size_name:
        try:
            size_obj = Size.objects.get(product=product, name=size_name)
            
            product_id_str = str(product.id)
            unique_id = f"{product_id_str}_{size_name}"
            
            cart_item = cart.cart.get(unique_id, {})
            current_qty = cart_item.get('quantity', 0)
            
            if current_qty + quantity > size_obj.stock:
                messages.error(request, f"Максимум {size_obj.stock} шт.", extra_tags=unique_id)
                return redirect('products:product_detail', slug=product.slug)
                
        except Size.DoesNotExist:
             messages.error(request, "Размер не найден", extra_tags='global_error')
             return redirect('products:product_detail', slug=product.slug)
    
    cart.add(product=product, quantity=quantity, size=size_name)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size', None)
    
    cart.remove(product, size=size)
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    size_name = request.POST.get('size', None)
    
    product_id_str = str(product.id)
    unique_id = f"{product_id_str}_{size_name}" if size_name else product_id_str

    if size_name and quantity > 0:
        try:
            size_obj = Size.objects.get(product=product, name=size_name)
            if quantity > size_obj.stock:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f"Максимум {size_obj.stock} шт.",
                        'max_stock': size_obj.stock
                    })
                
                messages.error(request, f"Максимум {size_obj.stock} шт.", extra_tags=unique_id)
                return redirect('cart:cart_detail')
        except Size.DoesNotExist:
            pass

    if quantity > 0:
        cart.add(product=product, quantity=quantity, size=size_name, override_quantity=True)
    else:
        cart.remove(product, size=size_name)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item = cart.cart.get(unique_id)
        item_total = Decimal(item['price']) * item['quantity'] if item else 0
        
        return JsonResponse({
            'success': True,
            'quantity': item['quantity'] if item else 0,
            'item_total': f"{item_total} ₽",
            'cart_total': f"{cart.get_total_price()} ₽",
            'cart_count': len(cart)
        })
        
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    recommended_products = Product.objects.order_by('?')[:8]
    
    return render(request, 'cart/detail.html', {
        'cart': cart,
        'recommended_products': recommended_products
    })
