from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, size=None, override_quantity=False):
        product_id = str(product.id)
        if size:
            unique_id = f"{product_id}_{size}"
        else:
            unique_id = product_id
            
        if unique_id not in self.cart:
            self.cart[unique_id] = {
                'quantity': 0, 
                'price': str(product.price),
                'size': size,
                'product_id': product_id
            }
            
        if override_quantity:
            self.cart[unique_id]['quantity'] = quantity
        else:
            self.cart[unique_id]['quantity'] += quantity
        self.save()

    def remove(self, product, size=None):
        product_id = str(product.id)
        if size:
            unique_id = f"{product_id}_{size}"
        else:
            unique_id = product_id
            
        if unique_id in self.cart:
            del self.cart[unique_id]
            self.save()
            
    def remove_by_id(self, unique_id):
        if unique_id in self.cart:
            del self.cart[unique_id]
            self.save()

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        
        product_map = {str(p.id): p for p in products}
        
        cart_copy = self.cart.copy()
        
        for unique_id, item in cart_copy.items():
            product = product_map.get(item['product_id'])
            if product:
                item['product'] = product
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                item['unique_id'] = unique_id
                yield item
            else:
                pass

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_shipping_cost(self):
        total = self.get_total_price()
        if total < 10000:
            return Decimal('700.00')
        return Decimal('0.00')

    def get_final_price(self):
        return self.get_total_price() + self.get_shipping_cost()

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True


