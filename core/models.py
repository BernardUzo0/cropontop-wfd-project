from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Farm Owner'),
        ('MANAGER', 'Farm Manager'),
        ('WORKER', 'Field Worker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.full_name} - {self.role}'


class Farm(models.Model):
    farm_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    size_acres = models.DecimalField(max_digits=8, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_farms')

    def __str__(self):
        return self.farm_name


class Field(models.Model):
    field_name = models.CharField(max_length=100)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='fields')
    crop_type = models.CharField(max_length=100)
    area_size = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.field_name


class Project(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
    ]

    project_name = models.CharField(max_length=120)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='projects')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects_created')

    def __str__(self):
        return self.project_name

    def completion_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='COMPLETED').count()
        return int((completed_tasks / total_tasks) * 100)


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')

    def __str__(self):
        return self.title


class TaskUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    progress_note = models.CharField(max_length=150)
    update_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Update for {self.task.title}'