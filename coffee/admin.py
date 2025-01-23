from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'roast_level', 'price', 'created_at')
    list_filter = ('roast_level', 'origin')
    search_fields = ('name', 'description', 'flavor_profile')
    readonly_fields = ('created_at', 'updated_at')
    boolean_field = ('is_published', 'hotitem')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price',),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('origin', 'roast_level', 'flavor_profile', 'image'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_published', 'hotitem'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Product, ProductAdmin)
