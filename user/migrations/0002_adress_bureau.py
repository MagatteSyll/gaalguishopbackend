# Generated by Django 4.0.2 on 2022-07-19 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adress',
            name='bureau',
            field=models.BooleanField(default=False),
        ),
    ]
