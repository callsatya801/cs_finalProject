from django.contrib import admin

from .models import Project, Bucket, Task, TaskComment, UserProject

# Register your models here.

admin.site.register(Project)
admin.site.register(Bucket)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(UserProject)
