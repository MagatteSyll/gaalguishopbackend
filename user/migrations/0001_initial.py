# Generated by Django 4.0.2 on 2022-07-19 06:03

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('produit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('prenom', models.CharField(max_length=100)),
                ('nom', models.CharField(max_length=100)),
                ('conform_phone', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('room', autoslug.fields.AutoSlugField(editable=False, populate_from=user.models.random_string_generator, unique=True)),
                ('group', autoslug.fields.AutoSlugField(editable=False, populate_from=user.models.random_string_generator, unique=True)),
                ('channel', autoslug.fields.AutoSlugField(editable=False, populate_from=user.models.random_string_generator, unique=True)),
                ('isbureaucrate', models.BooleanField(default=False)),
                ('istechnique', models.BooleanField(default=False)),
                ('is_employe_simple', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Adress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adress', models.CharField(max_length=255)),
                ('banlieu', models.BooleanField(default=False)),
                ('centre', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CodeConfirmationPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('code', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Pays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pays', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=255)),
                ('pays', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.pays')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('lu', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('nature_notification', models.CharField(blank=True, choices=[('avertissement', 'avertissement'), ('etat commande', 'etat commande'), ('vente', 'vente'), ('annulation d achat', 'annulation d achat'), ('annulation de vente', 'annulation de vente'), ('desactivation boutique', 'desactivation boutique'), ('pour follower', 'pour follower'), ('note vendeur', 'note vendeur'), ('reactivation boutique', 'reactivation boutique'), ('probleme technique', 'probleme technique')], max_length=255)),
                ('commande', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='produit.commande')),
                ('produit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='produit.produit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('lieu_travail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.adress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Avertissement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.PositiveIntegerField(default=0)),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.employe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='adress',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.region'),
        ),
        migrations.CreateModel(
            name='ActionStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField()),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.employe')),
            ],
        ),
    ]
