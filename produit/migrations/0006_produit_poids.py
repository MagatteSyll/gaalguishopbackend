# Generated by Django 4.0.2 on 2022-08-08 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produit', '0005_boutique_comptegaalguimoney'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='poids',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=19),
        ),
    ]
