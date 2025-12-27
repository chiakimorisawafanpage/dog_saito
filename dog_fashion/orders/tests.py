from django.test import TestCase
from django.urls import reverse

from products.models import Product, Category
from cart.cart import Cart
from .models import Order, OrderItem


class OrderViewsUITests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Outerwear", slug="outerwear")
        self.product = Product.objects.create(
            name="Raincoat Yellow",
            slug="raincoat-yellow",
            description="Warm and waterproof.",
            price="2500.00",
            available=True,
        )
        self.product.categories.add(category)

    def _add_item_to_cart_session(self):
        session = self.client.session
        request = type("Req", (), {"session": session})
        cart = Cart(request)
        cart.add(self.product, quantity=2)
        session.save()

    def test_order_create_get_shows_checkout_ui(self):
        self._add_item_to_cart_session()

        url = reverse("orders:order_create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order/create.html")

        self.assertContains(response, "Контакты")
        self.assertContains(response, "Доставка")
        self.assertContains(response, "Оплатить заказ")

    def test_order_create_post_creates_order_and_shows_success_page(self):
        self._add_item_to_cart_session()

        url = reverse("orders:order_create")
        payload = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "address": "Main street 1",
            "city": "Moscow",
            "postal_code": "123456",
        }
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order/created.html")

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertTrue(order.paid)
        self.assertEqual(order.email, "test@example.com")

        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)
        item = OrderItem.objects.get(order=order)
        self.assertEqual(item.product, self.product)

        self.assertContains(response, f"#{order.id}")
        self.assertContains(response, "Вернуться в магазин")
