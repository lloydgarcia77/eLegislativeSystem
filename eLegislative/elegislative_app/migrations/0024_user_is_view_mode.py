# Generated by Django 3.1.5 on 2021-01-30 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elegislative_app', '0023_auto_20210129_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_view_mode',
            field=models.BooleanField(default=False, verbose_name='View Mode Only'),
        ),
    ]