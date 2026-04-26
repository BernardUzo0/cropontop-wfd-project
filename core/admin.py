from django.contrib import admin
from .models import UserProfile, Farm, Field, Project, Task, TaskUpdate

admin.site.register(UserProfile)
admin.site.register(Farm)
admin.site.register(Field)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TaskUpdate)