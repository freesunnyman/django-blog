from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("名称", max_length=100, unique=True)
    slug = models.SlugField("URL标识", max_length=120, unique=True, blank=True)
    description = models.TextField("描述", blank=True)
    created_at = models.DateTimeField("创建时间", default=timezone.now, editable=False)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or "category"
        super().save(*args, **kwargs)
    
    @property
    def published_posts_count(self):
        return self.posts.filter(published=True).count()


class Post(models.Model):
    class SourceType(models.TextChoices):
        MARKDOWN = "markdown", "Markdown"
        PDF = "pdf", "PDF"

    category = models.ForeignKey(
        Category,
        verbose_name="分类",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    title = models.CharField("标题", max_length=200)
    slug = models.SlugField("URL标识", max_length=220, unique=True, blank=True)

    source_type = models.CharField(
        "来源类型",
        max_length=20,
        choices=SourceType.choices,
        db_index=True
    )
    source_file = models.FileField("源文件", upload_to="document/")

    content_markdown = models.TextField("Markdown内容", blank=True)
    content_text = models.TextField("文本内容", blank=True)
    content_html = models.TextField("HTML内容", blank=True)

    created_at = models.DateTimeField("创建时间", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    published = models.BooleanField("已发布", default=True, db_index=True)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "post"
            slug = base
            i = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)
