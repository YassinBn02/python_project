# Generated by Django 5.1.3 on 2024-11-15 10:36

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('birth', models.DateField()),
                ('password', models.CharField(max_length=255)),
                ('role', models.SmallIntegerField(choices=[(0, 'Admin'), (1, 'Member')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='event_images/')),
                ('category', models.CharField(max_length=200)),
                ('status', models.SmallIntegerField(choices=[(0, 'Pending'), (1, 'Published'), (2, 'Blocked')], default=0)),
                ('total_number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('favorites', models.ManyToManyField(blank=True, related_name='favorited_events', to='app_1.user')),
                ('members', models.ManyToManyField(blank=True, related_name='joined_events', to='app_1.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_events', to='app_1.user')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('rate', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app_1.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app_1.user')),
            ],
        ),
    ]