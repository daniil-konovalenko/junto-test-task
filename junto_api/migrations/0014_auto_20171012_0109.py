# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-11 22:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('junto_api', '0013_auto_20171011_2302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'категория', 'verbose_name_plural': 'категории'},
        ),
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name': 'блюдо', 'verbose_name_plural': 'блюда'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'заказ', 'verbose_name_plural': 'заказы'},
        ),
        migrations.AlterModelOptions(
            name='restaurant',
            options={'verbose_name': 'ресторан', 'verbose_name_plural': 'рестораны'},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='categories',
            field=models.ManyToManyField(related_name='dishes', related_query_name='dish', to='junto_api.Category', verbose_name='категории'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='name',
            field=models.CharField(max_length=200, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='стоимость, ₽'),
        ),
        migrations.AlterField(
            model_name='dishorder',
            name='current_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='стоимость на момент заказа, ₽'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(editable=False, verbose_name='время создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', related_query_name='order', to=settings.AUTH_USER_MODEL, verbose_name='оператор'),
        ),
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', related_query_name='orders', to='junto_api.Restaurant', verbose_name='ресторан'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Ожидает оплаты'), (1, 'Оплачен'), (2, 'Отменён')], default=0, verbose_name='статус'),
        ),
        migrations.AlterField(
            model_name='refreshtoken',
            name='value',
            field=models.CharField(db_index=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='city',
            field=models.CharField(max_length=50, verbose_name='город'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(max_length=200, verbose_name='название'),
        ),
    ]
