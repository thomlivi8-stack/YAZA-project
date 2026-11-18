from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_materials, name='category_materials'),
    path('category/<slug:cat_slug>/<slug:slug>/', views.material_detail, name='material_detail'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmark/toggle/<int:material_id>/', views.toggle_bookmark, name='toggle_bookmark'),
]