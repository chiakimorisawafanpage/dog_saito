from django.contrib import admin
from .models import Category, Product, Size, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'categories']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SizeInline, ProductImageInline]
    filter_horizontal = ('categories',)
