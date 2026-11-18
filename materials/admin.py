from django.contrib import admin
from .models import Category, Material, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'page_count', 'file_size', 'created_at']
    readonly_fields = ['thumbnail', 'page_count', 'file_size', 'slug']
    list_filter = ['category']
    #prepopulated_fields = {'slug': ('title',)}

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'material', 'created_at']
    list_filter = ['created_at']