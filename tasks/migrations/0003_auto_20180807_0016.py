# Generated by Django 2.0.7 on 2018-08-07 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_bucket_seq'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='dueDate',
            field=models.DateField(blank=True),
        ),
    ]
