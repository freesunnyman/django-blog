from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("p/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("c/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
]

