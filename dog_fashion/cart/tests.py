from django.test import TestCase
from django.urls import reverse

from products.models import Product, Category
from .cart import Cart


class CartViewsUITests(TestCase):
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

    def test_cart_detail_empty_shows_empty_message(self):
        url = reverse("cart:cart_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart/detail.html")
        self.assertContains(response, "Здесь пока ничего нет")

        cart = response.context["cart"]
        self.assertEqual(len(cart), 0)

    def test_cart_add_and_detail_show_item_and_checkout_button(self):
        add_url = reverse("cart:cart_add", args=[self.product.id])
        response = self.client.post(add_url, {"quantity": 1}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart/detail.html")

        cart = response.context["cart"]
        self.assertEqual(len(cart), 1)

        self.assertContains(response, "ТВОЯ КОРЗИНА")
        self.assertContains(response, self.product.name)
        self.assertContains(response, "Перейти к оплате")

    def test_cart_detail_has_recommended_products_section(self):
        for i in range(3):
            Product.objects.create(
                name=f"Accessory {i}",
                slug=f"accessory-{i}",
                description="Accessory",
                price="1000.00",
                available=True,
            ).categories.add(Category.objects.get(slug="outerwear"))

        url = reverse("cart:cart_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Potrebbero interessarti")
