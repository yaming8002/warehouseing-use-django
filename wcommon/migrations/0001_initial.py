# Generated by Django 5.0.1 on 2024-04-17 07:23

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='名稱')),
                ('is_active', models.BooleanField(default='True')),
            ],
            options={
                'verbose_name': 'ugroup',
                'verbose_name_plural': 'ugroups',
            },
        ),
        migrations.CreateModel(
            name='SysInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, verbose_name='代號')),
                ('name', models.CharField(max_length=50, verbose_name='參數名稱')),
                ('value', models.CharField(max_length=50, verbose_name='系統數值')),
            ],
            options={
                'unique_together': {('code', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='選單名稱')),
                ('url', models.CharField(max_length=255, verbose_name='選單URL')),
                ('category', models.IntegerField(verbose_name='分類代號')),
                ('order', models.IntegerField(verbose_name='順序')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcommon.usergroup', verbose_name='權限組')),
            ],
        ),
        migrations.CreateModel(
            name='Muser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username_zh', models.CharField(default='', max_length=30, verbose_name='姓名')),
                ('unit', models.CharField(max_length=30, null=True, verbose_name='所屬單位')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_staff', models.BooleanField(default='True')),
                ('is_active', models.BooleanField(default='True')),
                ('is_superuser', models.BooleanField(default='False')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcommon.usergroup', verbose_name='權限組')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
