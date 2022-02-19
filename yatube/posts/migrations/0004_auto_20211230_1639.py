# Generated by Django 2.2.19 on 2021-12-30 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20211230_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='slug',
            field=models.CharField(default=True, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='title',
            field=models.CharField(default=True, max_length=100),
            preserve_default=False,
        ),
    ]
