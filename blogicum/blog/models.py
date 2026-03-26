from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    title = models.CharField('Название', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор', unique=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField('Название места', max_length=256)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    is_published = models.BooleanField('Опубликовано', default=True)
    image = models.ImageField('Изображение', upload_to='posts_images/', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий к {self.post.title}'