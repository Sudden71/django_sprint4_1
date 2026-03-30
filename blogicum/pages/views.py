from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from blogicum.forms import RegistrationForm
from blog.models import Post


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
        else:
            # ← ← ДОБАВЬ ЭТО!
            print(" Ошибки формы:", form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


def profile(request, username):
    """Страница профиля пользователя"""
    profile_user = get_object_or_404(User, username=username)
    
    # Автор видит все свои посты, остальные — только опубликованные
    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_owner': request.user == profile_user,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        return redirect('pages:profile', username=request.user.username)
    
    return render(request, 'registration/edit_profile.html')