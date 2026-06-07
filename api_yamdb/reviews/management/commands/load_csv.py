import csv

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


DATA_DIR = settings.BASE_DIR / 'static' / 'data'


class Command(BaseCommand):
    help = 'Загрузка данных из CSV'

    def handle(self, *args, **options):

        loaders = {
            'users.csv': self.load_users,
            'category.csv': self.load_categories,
            'genre.csv': self.load_genres,
            'titles.csv': self.load_titles,
            'genre_title.csv': self.load_genre_title,
            'review.csv': self.load_reviews,
            'comments.csv': self.load_comments,
        }

        for loader in loaders.values():
            loader()

        self.stdout.write(
            self.style.SUCCESS('Данные успешно загружены!')
        )

    def load_users(self):
        with open(DATA_DIR / 'users.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                User.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'bio': row['bio'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                    }
                )

    def load_categories(self):
        with open(DATA_DIR / 'category.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Category.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )

    def load_genres(self):
        with open(DATA_DIR / 'genre.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Genre.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )

    def load_titles(self):
        with open(DATA_DIR / 'titles.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Title.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': Category.objects.get(pk=row['category']),
                    }
                )

    def load_genre_title(self):
        with open(DATA_DIR / 'genre_title.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                title = Title.objects.get(pk=row['title_id'])
                genre = Genre.objects.get(pk=row['genre_id'])

                title.genre.add(genre)

    def load_reviews(self):
        with open(DATA_DIR / 'review.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Review.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'title': Title.objects.get(pk=row['title_id']),
                        'author': User.objects.get(pk=row['author']),
                        'text': row['text'],
                        'score': row['score'],
                        'pub_date': row['pub_date'],
                    }
                )

    def load_comments(self):
        with open(DATA_DIR / 'comments.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Comment.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'review': Review.objects.get(pk=row['review_id']),
                        'author': User.objects.get(pk=row['author']),
                        'text': row['text'],
                        'pub_date': row['pub_date'],
                    }
                )
