# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-29 14:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Nic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nic_name', models.CharField(max_length=250)),
                ('location', models.CharField(max_length=250)),
                ('ip_configuration_name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Ressources',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupe_name', models.CharField(max_length=250)),
                ('location', models.CharField(max_length=250)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Storages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_account_name', models.CharField(max_length=250)),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Ressources')),
            ],
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subnet_name', models.CharField(max_length=250)),
                ('address_prefixes', models.CharField(max_length=250)),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Ressources')),
            ],
        ),
        migrations.CreateModel(
            name='UserCloud',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_azure', models.CharField(max_length=500)),
                ('password_azure', models.CharField(max_length=500)),
                ('subscription_id', models.CharField(max_length=500)),
                ('client_id', models.CharField(max_length=500)),
                ('secret', models.CharField(max_length=500)),
                ('tenant', models.CharField(max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vnet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vnet_name', models.CharField(max_length=250)),
                ('location', models.CharField(max_length=250)),
                ('address_prefixes', models.CharField(max_length=250)),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Ressources')),
            ],
        ),
        migrations.AddField(
            model_name='subnet',
            name='vnet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Vnet'),
        ),
        migrations.AddField(
            model_name='nic',
            name='ressource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Ressources'),
        ),
        migrations.AddField(
            model_name='nic',
            name='subnet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Subnet'),
        ),
        migrations.AddField(
            model_name='nic',
            name='vnet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ressource.Vnet'),
        ),
    ]
