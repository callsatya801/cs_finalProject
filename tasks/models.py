from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class Project(models.Model):

    def get_sentinel_user():
        return get_user_model().objects.get_or_create(username='unknown')[0]

    TYPES =( ('P', 'Personal'),
             ('T', 'Team')
        )
    STATUSES =( ('A', 'Active'),
             ('D', 'Archive')
        )
    name = models.CharField(max_length=200)
    p_type = models.CharField(max_length=1, choices=TYPES)
    status = models.CharField(max_length=1, choices=STATUSES)
    creationDate = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )

    def __str__(self):
        return f"{self.id}:{self.name}:{self.p_type}:{self.status}:{self.creationDate}:{self.owner}"

# Holds  - Planned, In Progress, Completed as default-
#It can be exteneded to any number of buckets to classify the Tasks in the project
class Bucket(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    seq = models.IntegerField()

    def __str__(self):
        return f"{self.id}:{self.project}:{self.name}"


class Task(models.Model):
    def get_sentinel_user():
        return get_user_model().objects.get_or_create(username='unknown')[0]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projects')
    bucket =  models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='buckets')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    creationDate = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    dueDate = models.DateField(blank=True)
    assignedTo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name = 'assignee'
    )

    def __str__(self):
        return f"{self.id}:{self.project}:{self.bucket}:{self.title}:{self.description}:{self.creationDate}:{self.owner}:{self.dueDate}:{self.assignedTo}"

class TaskComment(models.Model):
    def get_sentinel_user():
        return get_user_model().objects.get_or_create(username='unknown')[0]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tasks')
    comment = models.CharField(max_length=500)
    commentedBy= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
    )
    commentedOn=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}:{self.task}:{self.comment}:{self.commentedBy}:{self.commentedOn}"


class UserProject(models.Model):
    def get_sentinel_user():
        return get_user_model().objects.get_or_create(username='unknown')[0]

    ROLES =( ('A', 'Admin'),
             ('M', 'Member')
        )

    user= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLES)

    def __str__(self):
        return f"{self.id}:{self.user}:{self.project}:{self.role}"
