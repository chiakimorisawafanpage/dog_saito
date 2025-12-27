from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Size


class ProductViewsUITests(TestCase):
    def setUp(self):
        self.category_root = Category.objects.create(
            name="Outerwear", slug="outerwear"
        )
        self.category_new = Category.objects.create(
            name="New Arrivals", slug="new-arrivals"
        )

        self.product_1 = Product.objects.create(
            name="Raincoat Yellow",
            slug="raincoat-yellow",
            description="Warm and waterproof.",
            price="2500.00",
            available=True,
        )
        self.product_1.categories.add(self.category_root, self.category_new)

        self.product_2 = Product.objects.create(
            name="Sweater Red",
            slug="sweater-red",
            description="Soft sweater.",
            price="1800.00",
            available=True,
        )
        self.product_2.categories.add(self.category_root)
        Size.objects.create(product=self.product_1, name="S", stock=5)
        Size.objects.create(product=self.product_1, name="M", stock=0)
        Size.objects.create(product=self.product_2, name="M", stock=3)

    def test_index_status_and_template(self):
        url = reverse("products:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/index.html")

    def test_index_hero_and_marquee_ui_elements(self):
        url = reverse("products:index")
        response = self.client.get(url)

        self.assertContains(response, "Dog Fashion")
        self.assertContains(response, "Dog Fashion<br>Collection")
        self.assertContains(response, "Discover")

        self.assertContains(response, "Dog Fashion")
        self.assertContains(response, "New Arrivals")
        self.assertContains(response, "Accessories")
        self.assertContains(response, "Raincoats")

    def test_index_product_slider_uses_new_arrivals_and_swiper_js(self):
        url = reverse("products:index")
        response = self.client.get(url)

        self.assertIn("products", response.context)
        products = list(response.context["products"])
        self.assertIn(self.product_1, products)

        self.assertContains(response, 'class="swiper productSwiper"', status_code=200)
        self.assertContains(response, 'var productSwiper = new Swiper(".productSwiper"', status_code=200)

    def test_product_list_header_ui(self):
        url = reverse(
            "products:product_list_by_category", args=[self.category_root.slug]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/list.html")

        self.assertContains(response, self.category_root.name, status_code=200)
        self.assertContains(response, "Home")
        self.assertContains(response, "Filter")

    def test_product_list_grid_contains_aesthetic_image_and_products(self):
        url = reverse(
            "products:product_list_by_category", args=[self.category_root.slug]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Estetica")

        self.assertIn("products", response.context)
        products = list(response.context["products"])
        self.assertIn(self.product_1, products)
        self.assertIn(self.product_2, products)

    def test_product_list_size_filter_works(self):
        url = reverse(
            "products:product_list_by_category",
            args=[self.category_root.slug],
        )
        response = self.client.get(url, {"size": ["S"]})

        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertIn(self.product_1, products)
        self.assertNotIn(self.product_2, products)

        self.assertIn("available_sizes", response.context)
        self.assertIn("selected_sizes", response.context)
        self.assertIn("S", response.context["selected_sizes"])

    def test_product_detail_main_info_and_add_to_cart_ui(self):
        url = reverse("products:product_detail", args=[self.product_1.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/detail.html")

        self.assertContains(response, self.product_1.name)
        self.assertContains(response, f"{self.product_1.price} ₽")
        self.assertContains(response, "Добавить в корзину")

        self.assertContains(response, "Size", status_code=200)
        self.assertContains(response, 'type="radio"', status_code=200)

    def test_product_detail_related_products_block_and_title(self):
        related = Product.objects.create(
            name="Raincoat Green",
            slug="raincoat-green",
            description="Another coat.",
            price="2600.00",
            available=True,
        )
        related.categories.add(self.category_root)

        url = reverse("products:product_detail", args=[self.product_1.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "С этим товаром покупают")

        self.assertIn("related_products", response.context)
        related_qs = list(response.context["related_products"])
        self.assertIn(related, related_qs)
