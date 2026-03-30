from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User


# ==================== УТИЛИТЫ ====================

def get_published_posts_queryset():
    """Базовый queryset для опубликованных постов"""
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def paginate_posts(request, queryset, per_page=10):
    """Унифицированная функция пагинации"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# ==================== ВЬЮХИ ====================

def index(request):
    """Главная страница"""
    posts = get_published_posts_queryset().order_by('-pub_date')
    page_obj = paginate_posts(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Страница публикации с проверкой прав доступа"""
    post = get_object_or_404(
        Post.objects.select_related('category', 'author').prefetch_related('comments'),
        id=post_id
    )
    
    # 🔐 Проверка прав: если пост не опубликован или дата в будущем — только автор
    if not (post.is_published and post.pub_date <= timezone.now()):
        if request.user != post.author:
            raise Http404("Публикация не найдена")
    
    # Комментарии (у Comment нет is_published)
    comments = post.comments.select_related('author').order_by('created_at')
    
    # Обработка формы комментария
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, category_slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    
    # Используем общую функцию + фильтр по категории + comment_count
    posts = get_published_posts_queryset().filter(category=category).order_by('-pub_date')
    page_obj = paginate_posts(request, posts)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


@login_required
def profile(request, username=None):
    """Страница профиля пользователя"""
    user = get_object_or_404(User, username=username) if username else request.user
    
    # Посты пользователя
    posts = get_published_posts_queryset().filter(author=user).order_by('-pub_date')
    
    # Общее количество постов (до пагинации)
    total_posts = posts.count()
    
    page_obj = paginate_posts(request, posts)
    
    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'page_obj': page_obj,
        'total_posts': total_posts,  
    })

@login_required
def create_post(request):
    """Создание новой публикации"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', post_id=post.id)
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование публикации"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    """Удаление публикации"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=comment.post.id)
    
    post_id = comment.post.id
    comment.delete()
    return redirect('blog:post_detail', post_id=post_id)


def test_email(request):
    """Тест отправки email"""
    send_mail(
        'Тестовое письмо от Блогикум',
        'Это тестовое письмо. Если вы его видите — email настроен!',
        settings.DEFAULT_FROM_EMAIL,
        ['admin@blogicum.ru'],
        fail_silently=False,
    )
    return HttpResponse('Письмо отправлено! Открой папку sent_emails/ и проверь.')