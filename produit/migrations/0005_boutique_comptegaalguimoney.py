# Generated by Django 4.0.2 on 2022-08-07 07:21

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('produit', '0004_commande_codeid'),
    ]

    operations = [
        migrations.AddField(
            model_name='boutique',
            name='comptegaalguimoney',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]