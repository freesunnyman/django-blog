from __future__ import annotations

import io
import os
import re
from datetime import datetime

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from django import forms

import markdown as md
from pypdf import PdfReader

from .models import Post, Category


class PostAdminForm(forms.ModelForm):
    folder_upload = forms.FileField(
        required=False,
        widget=forms.widgets.Input(
            attrs={
                'type': 'file',
                'webkitdirectory': True,
                'directory': True,
                'multiple': True,
                'id': 'folder_upload'
            }
        ),
        help_text="选择整个图片文件夹上传（推荐）"
    )
    image_1 = forms.FileField(required=False, help_text="图片 1（可选）")
    image_2 = forms.FileField(required=False, help_text="图片 2（可选）")
    image_3 = forms.FileField(required=False, help_text="图片 3（可选）")
    image_4 = forms.FileField(required=False, help_text="图片 4（可选）")
    image_5 = forms.FileField(required=False, help_text="图片 5（可选）")
    image_6 = forms.FileField(required=False, help_text="图片 6（可选）")
    image_7 = forms.FileField(required=False, help_text="图片 7（可选）")
    image_8 = forms.FileField(required=False, help_text="图片 8（可选）")
    image_9 = forms.FileField(required=False, help_text="图片 9（可选）")
    image_10 = forms.FileField(required=False, help_text="图片 10（可选）")
    image_11 = forms.FileField(required=False, help_text="图片 11（可选）")
    image_12 = forms.FileField(required=False, help_text="图片 12（可选）")
    image_13 = forms.FileField(required=False, help_text="图片 13（可选）")
    image_14 = forms.FileField(required=False, help_text="图片 14（可选）")
    image_15 = forms.FileField(required=False, help_text="图片 15（可选）")
    image_16 = forms.FileField(required=False, help_text="图片 16（可选）")
    image_17 = forms.FileField(required=False, help_text="图片 17（可选）")
    image_18 = forms.FileField(required=False, help_text="图片 18（可选）")
    image_19 = forms.FileField(required=False, help_text="图片 19（可选）")
    image_20 = forms.FileField(required=False, help_text="图片 20（可选）")
    
    class Meta:
        model = Post
        fields = '__all__'


def _read_uploaded_file_as_bytes(f) -> bytes:
    pos = f.tell()
    try:
        f.seek(0)
        return f.read()
    finally:
        try:
            f.seek(pos)
        except Exception:
            pass


def _save_image(image_file, image_name: str) -> str:
    date_path = datetime.now().strftime("%Y/%m/%d")
    upload_path = f"image/{date_path}/{image_name}"
    
    if default_storage.exists(upload_path):
        name, ext = os.path.splitext(image_name)
        counter = 1
        while default_storage.exists(f"image/{date_path}/{name}_{counter}{ext}"):
            counter += 1
        upload_path = f"image/{date_path}/{name}_{counter}{ext}"
    
    saved_path = default_storage.save(upload_path, image_file)
    return f"{settings.MEDIA_URL}{saved_path}"


def _process_images(markdown_content: str, request_files) -> tuple[str, list[str]]:
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    processed_content = markdown_content
    uploaded_images = []
    
    images_found = image_pattern.findall(markdown_content)
    
    uploaded_files = {}
    
    if 'folder_upload' in request_files:
        files = request_files.getlist('folder_upload')
        for f in files:
            if f and f.name:
                filename = os.path.basename(f.name)
                uploaded_files[filename] = f
    
    image_fields = [
        'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
        'image_6', 'image_7', 'image_8', 'image_9', 'image_10',
        'image_11', 'image_12', 'image_13', 'image_14', 'image_15',
        'image_16', 'image_17', 'image_18', 'image_19', 'image_20'
    ]
    for field_name in image_fields:
        if field_name in request_files:
            f = request_files[field_name]
            if f and f.name:
                filename = os.path.basename(f.name)
                if filename not in uploaded_files:
                    uploaded_files[filename] = f
    
    for alt_text, image_path in images_found:
        if image_path.startswith(('http://', 'https://', 'data:')):
            continue
        
        image_filename = os.path.basename(image_path)
        
        if image_filename in uploaded_files:
            image_file = uploaded_files[image_filename]
            new_url = _save_image(image_file, image_filename)
            
            old_pattern = f'![{alt_text}]({image_path})'
            new_pattern = f'![{alt_text}]({new_url})'
            processed_content = processed_content.replace(old_pattern, new_pattern)
            uploaded_images.append(image_filename)
    
    return processed_content, uploaded_images


def _parse_markdown(uploaded_file, request_files=None) -> tuple[str, str, list[str]]:
    raw = _read_uploaded_file_as_bytes(uploaded_file).decode("utf-8", errors="replace")
    uploaded_images = []
    
    if request_files:
        raw, uploaded_images = _process_images(raw, request_files)
    
    html = md.markdown(raw, extensions=["fenced_code", "tables", "toc"])
    return raw, html, uploaded_images


def _parse_pdf(uploaded_file) -> str:
    data = _read_uploaded_file_as_bytes(uploaded_file)
    reader = PdfReader(io.BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "category", "source_type", "published", "created_at", "updated_at")
    list_filter = ("category", "source_type", "published", "created_at")
    search_fields = ("title", "slug", "content_markdown", "content_text")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "published")}),
        ("Source", {"fields": ("source_type", "source_file")}),
        ("Images", {"fields": ("folder_upload",), "description": "推荐使用文件夹上传，选择包含所有图片的文件夹"}),
        ("单个图片上传", {"fields": (
            "image_1", "image_2", "image_3", "image_4", "image_5",
            "image_6", "image_7", "image_8", "image_9", "image_10",
            "image_11", "image_12", "image_13", "image_14", "image_15",
            "image_16", "image_17", "image_18", "image_19", "image_20"
        ), "classes": ("collapse",)}),
        (
            "Parsed content (auto)",
            {"fields": ("content_markdown", "content_text", "content_html")},
        ),
    )
    readonly_fields = ("content_markdown", "content_text", "content_html")

    def save_model(self, request, obj: Post, form, change):
        uploaded = getattr(obj, "source_file", None)
        if uploaded:
            name = (uploaded.name or "").lower()
            if obj.source_type == Post.SourceType.MARKDOWN or name.endswith((".md", ".markdown")):
                obj.source_type = Post.SourceType.MARKDOWN
                
                obj.content_markdown, obj.content_html, uploaded_images = _parse_markdown(uploaded, request.FILES)
                
                if uploaded_images:
                    self.message_user(request, f"成功上传并处理了 {len(uploaded_images)} 张图片: {', '.join(uploaded_images)}")
                else:
                    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
                    images_found = image_pattern.findall(obj.content_markdown)
                    if images_found:
                        self.message_user(request, f"注意：Markdown中找到 {len(images_found)} 张图片引用，但没有匹配的图片文件被上传。")
                
                obj.content_text = ""
            elif obj.source_type == Post.SourceType.PDF or name.endswith(".pdf"):
                obj.source_type = Post.SourceType.PDF
                try:
                    obj.content_text = _parse_pdf(uploaded)
                except Exception as e:
                    raise ValidationError(f"PDF 解析失败: {e}") from e
                obj.content_markdown = ""
                obj.content_html = ""
            else:
                raise ValidationError("仅支持上传 .md/.markdown 或 .pdf 文件")

        super().save_model(request, obj, form, change)
