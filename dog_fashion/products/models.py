from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_new(self):
        return any(c.slug == 'new-arrivals' for c in self.categories.all())

    def get_size_guide_type(self):
        for category in self.categories.all():
            cat = category
            while cat:
                slug = cat.slug.lower()
                if 'shoes' in slug or 'boots' in slug or 'footwear' in slug:
                    return 'shoes'
                if 'acc-' in slug or 'accessories' in slug:
                    return 'accessories'
                cat = cat.parent
        
        return 'clothing'

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Size(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}"
