
from django.contrib.auth.models import User
from news.models import Author, Category, Post, PostCategory, Comment
from datetime import datetime

# пользователи
print("Создаем пользователей...")
user1 = User.objects.create_user('john_doe')
user2 = User.objects.create_user('jane_smith')
print(f"Созданы пользователи: {user1.username}, {user2.username}")

# авторы
print("\nСоздаем авторов...")
author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)
print(f"Авторы созданы: {author1.user.username}, {author2.user.username}")

# категории
print("\nСоздаем категории...")
category_sports = Category.objects.create(name='Спорт')
category_politics = Category.objects.create(name='Политика')
category_education = Category.objects.create(name='Образование')
category_tech = Category.objects.create(name='Технологии')
print(f"Категории созданы: {category_sports.name}, {category_politics.name}, {category_education.name}, {category_tech.name}")

# посты
print("\nСоздаем посты...")

# Статья 1
post1 = Post.objects.create(
    author=author1,
    post_type='AR',  # AR - статья
    title='Влияние технологий на образование',
    content='Современные технологии кардинально меняют подход к образованию. Онлайн-курсы, интерактивные доски и искусственный интеллект становятся неотъемлемой частью учебного процесса. Это позволяет сделать обучение более доступным и эффективным.',
    rating=0
)
# Добавляем категории (две категории для этой статьи)
PostCategory.objects.create(post=post1, category=category_education)
PostCategory.objects.create(post=post1, category=category_tech)
print(f'Создана статья: "{post1.title}" с категориями: Образование, Технологии')

# Статья 2
post2 = Post.objects.create(
    author=author2,
    post_type='AR',  # AR - статья
    title='Будущее спортивных технологий',
    content='Спортивная индустрия активно внедряет новые технологии. От систем видеофиксации до умных тренажеров - технологии помогают спортсменам достигать новых высот и делают спорт более зрелищным для болельщиков.',
    rating=0
)
PostCategory.objects.create(post=post2, category=category_sports)
PostCategory.objects.create(post=post2, category=category_tech)
print(f'Создана статья: "{post2.title}" с категориями: Спорт, Технологии')

# Новость
post3 = Post.objects.create(
    author=author1,
    post_type='NW',  # NW - новость
    title='Новый закон о образовании принят в парламенте',
    content='Сегодня парламент принял новый закон об образовании, который вводит обязательное использование цифровых технологий в школах. Закон также предусматривает увеличение финансирования образовательных учреждений.',
    rating=0
)
PostCategory.objects.create(post=post3, category=category_politics)
PostCategory.objects.create(post=post3, category=category_education)
print(f'Создана новость: "{post3.title}" с категориями: Политика, Образование')

# комментарии
print("\nСоздаем комментарии...")

# Комментарии к первой статье
comment1 = Comment.objects.create(
    post=post1,
    user=user2,
    text='Очень познавательная статья! Технологии действительно меняют образование.',
    rating=0
)
print(f'Комментарий 1 к статье "{post1.title}" от {user2.username}')

comment2 = Comment.objects.create(
    post=post1,
    user=user1,
    text='Спасибо за отзыв! Я тоже считаю, что это важно.',
    rating=0
)
print(f'Комментарий 2 к статье "{post1.title}" от {user1.username}')

# Комментарий ко второй статье
comment3 = Comment.objects.create(
    post=post2,
    user=user1,
    text='Интересная статья! А как насчет влияния технологий на подготовку спортсменов?',
    rating=0
)
print(f'Комментарий к статье "{post2.title}" от {user1.username}')

# Комментарий к новости
comment4 = Comment.objects.create(
    post=post3,
    user=user2,
    text='Наконец-то! Давно пора было принять такой закон.',
    rating=0
)
print(f'Комментарий к новости "{post3.title}" от {user2.username}')

print("\nПрименяем like/dislike...")

# Лайки/дизлайки к постам
post1.like()  # +1
post1.like()  # +1
post1.like()  # +1
post1.dislike()  # -1
print(f'Рейтинг статьи "{post1.title}" после лайков/дислайков: {post1.rating}')

post2.like()  # +1
post2.like()  # +1
print(f'Рейтинг статьи "{post2.title}" после лайков: {post2.rating}')

post3.like()  # +1
post3.dislike()  # -1
post3.dislike()  # -1
print(f'Рейтинг новости "{post3.title}" после лайков/дислайков: {post3.rating}')

# Лайки/дизлайки к комментариям
comment1.like()  # +1
comment1.like()  # +1
comment1.like()  # +1
print(f'Рейтинг комментария 1: {comment1.rating}')

comment2.like()  # +1
comment2.dislike()  # -1
print(f'Рейтинг комментария 2: {comment2.rating}')

comment3.like()  # +1
comment3.like()  # +1
comment3.like()  # +1
comment3.like()  # +1
print(f'Рейтинг комментария 3: {comment3.rating}')

comment4.like()  # +1
comment4.dislike()  # -1
comment4.dislike()  # -1
print(f'Рейтинг комментария 4: {comment4.rating}')

# обновление рейтингов
print("\nОбновляем рейтинги авторов...")
author1.update_rating()
author2.update_rating()
print(f'Рейтинг автора {author1.user.username}: {author1.rating}')
print(f'Рейтинг автора {author2.user.username}: {author2.rating}')

# лучший пользователь
print("\n" + "="*50)
print("ЛУЧШИЙ ПОЛЬЗОВАТЕЛЬ ПО РЕЙТИНГУ")
print("="*50)

best_author = Author.objects.order_by('-rating').first()
print(f'Username: {best_author.user.username}')
print(f'Рейтинг: {best_author.rating}')

# лучшая статья
print("\n" + "="*50)
print("ЛУЧШАЯ СТАТЬЯ (САМЫЙ ВЫСОКИЙ РЕЙТИНГ)")
print("="*50)

best_post = Post.objects.filter(post_type='AR').order_by('-rating').first()
print(f'Дата добавления: {best_post.created_at.strftime("%d.%m.%Y %H:%M")}')
print(f'Автор: {best_post.author.user.username}')
print(f'Рейтинг: {best_post.rating}')
print(f'Заголовок: {best_post.title}')
print(f'Превью: {best_post.preview()}')

# комментарии к лучшей статье
print("\n" + "="*50)
print(f"ВСЕ КОММЕНТАРИИ К СТАТЬЕ: {best_post.title}")
print("="*50)

comments_to_best_post = Comment.objects.filter(post=best_post).order_by('-created_at')
for comment in comments_to_best_post:
    print(f'\nДата: {comment.created_at.strftime("%d.%m.%Y %H:%M")}')
    print(f'Пользователь: {comment.user.username}')
    print(f'Рейтинг: {comment.rating}')
    print(f'Текст: {comment.text}')
    print("-" * 30)

# проверяем данные
print("\n" + "="*50)
print("ИТОГОВАЯ ПРОВЕРКА ВСЕХ ДАННЫХ")
print("="*50)

print(f"\nВсего пользователей: {User.objects.count()}")
print(f"Всего авторов: {Author.objects.count()}")
print(f"Всего категорий: {Category.objects.count()}")
print(f"Всего постов: {Post.objects.count()}")
print(f"  - Статей: {Post.objects.filter(post_type='AR').count()}")
print(f"  - Новостей: {Post.objects.filter(post_type='NW').count()}")
print(f"Всего комментариев: {Comment.objects.count()}")