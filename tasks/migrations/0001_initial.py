# Generated by Django 2.0.7 on 2018-08-04 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tasks.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('p_type', models.CharField(choices=[('P', 'Personal'), ('T', 'Team')], max_length=1)),
                ('status', models.CharField(choices=[('A', 'Active'), ('D', 'Archive')], max_length=1)),
                ('creationDate', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=models.SET(tasks.models.Project.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('creationDate', models.DateTimeField(auto_now=True)),
                ('dueDate', models.DateTimeField(blank=True)),
                ('assignedTo', models.ForeignKey(on_delete=models.SET(tasks.models.Task.get_sentinel_user), related_name='assignee', to=settings.AUTH_USER_MODEL)),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buckets', to='tasks.Bucket')),
                ('owner', models.ForeignKey(on_delete=models.SET(tasks.models.Task.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='tasks.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=500)),
                ('commentedOn', models.DateTimeField(auto_now=True)),
                ('commentedBy', models.ForeignKey(on_delete=models.SET(tasks.models.TaskComment.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.Task')),
            ],
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('A', 'Admin'), ('M', 'Member')], max_length=1)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.Project')),
                ('user', models.ForeignKey(on_delete=models.SET(tasks.models.UserProject.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='bucket',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.Project'),
        ),
    ]