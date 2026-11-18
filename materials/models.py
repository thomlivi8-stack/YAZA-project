from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.files.base import ContentFile
import pymupdf

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    cat_image = models.FileField(upload_to='cat_images/', blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_url(self):
        return reverse('category_materials', args=[self.slug])

    def __str__(self):
        return self.name

class Material(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='materials'
    )
    file = models.FileField(upload_to='materials/', blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    page_count = models.IntegerField(default=0)
    file_size = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # generate unique slug only once
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Material.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        # FIRST save to get file on disk
        super().save(*args, **kwargs)

        # SECOND part - thumbnail + metadata (only if file exists and thumbnail not yet created)
        if self.file and not self.thumbnail:
            try:
                size = self.file.size
                if size < 1024 * 1024:
                    self.file_size = f"{size / 1024:.0f} KB"
                else:
                    self.file_size = f"{size / (1024 * 1024):.1f} MB"

                self.file.open()
                pdf_bytes = self.file.read()
                self.file.close()

                doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
                self.page_count = len(doc)

                page = doc.load_page(0)
                pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                
                thumb_name = f"{self.slug}_thumb.png"
                self.thumbnail.save(thumb_name, ContentFile(pix.tobytes("png")), save=False)
                doc.close()

                # save only new fields, avoid infinite loop
                super().save(update_fields=['thumbnail', 'page_count', 'file_size'])

            except Exception as e:
                print(f"Thumbnail error for {self.title}: {e}")

    def get_url(self):
        return reverse('material_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.title

class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='bookmarked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'material')

    def __str__(self):
        return f"{self.user.username} - {self.material.title}"