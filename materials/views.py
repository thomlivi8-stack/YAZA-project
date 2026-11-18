from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Category, Material, Bookmark

# ==========================================
# HOMEPAGE
# ==========================================
def home(request):
    q = request.GET.get('q', '').strip()[:100]

    categories = Category.objects.all().order_by('name')

    materials_qs = Material.objects.select_related('category').order_by('-created_at')

    if q:
        materials_qs = materials_qs.filter(
            Q(title__icontains=q) |
            Q(category__name__icontains=q) |
            Q(slug__icontains=q)
        ).distinct()

    return render(request, 'home.html', {
        'categories': categories,
        'latest_materials': materials_qs[:12],
        'total_count': Material.objects.count(),
        'result_count': materials_qs.count(),
        'q': q,
    })

# ==========================================
# CATEGORY MATERIALS
# ==========================================
@login_required(login_url='/accounts/login/')
def category_materials(request, slug):
    category = get_object_or_404(Category, slug=slug)
    materials = Material.objects.filter(category=category).order_by('-created_at')
    return render(request, 'category.html', {
        'category': category,
        'materials': materials,
    })

# ==========================================
# MATERIAL DETAIL
# ==========================================
@login_required(login_url='/accounts/login/')
def material_detail(request, cat_slug, slug):
    material = get_object_or_404(Material, slug=slug, category__slug=cat_slug)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, material=material).exists()
    return render(request, 'material_detail.html', {
        'material': material,
        'is_bookmarked': is_bookmarked,
    })

# ==========================================
# BOOKMARKS
# ==========================================
@login_required(login_url='/accounts/login/')
def bookmarks(request):
    saved = Bookmark.objects.filter(user=request.user).select_related('material', 'material__category').order_by('-created_at')
    return render(request, 'bookmark.html', {
        'bookmarks': saved,
    })

# ==========================================
# TOGGLE BOOKMARK
# ==========================================
@login_required(login_url='/accounts/login/')
@require_POST
def toggle_bookmark(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, material=material)
    if not created:
        bookmark.delete()
    return redirect(material.get_url())

# ==========================================
# SEARCH - reuses home
# ==========================================
def search(request):
    return home(request)