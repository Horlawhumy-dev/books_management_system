# Generated by Django 4.2.16 on 2024-09-14 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminbook',
            name='borrowed_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]