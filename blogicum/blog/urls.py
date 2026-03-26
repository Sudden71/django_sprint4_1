from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('test-email/', views.test_email, name='test_email'),
]