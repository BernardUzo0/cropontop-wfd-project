from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Field, Project, Task, TaskUpdate
from .forms import RegisterForm, ProjectForm, TaskForm, FieldForm


def user_role(user):
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return None


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                role=form.cleaned_data['role']
            )
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    context = {
        'project_count': Project.objects.count(),
        'task_count': Task.objects.count(),
        'field_count': Field.objects.count(),
        'my_tasks_count': Task.objects.filter(assigned_to=request.user).count(),
        'completed_tasks': Task.objects.filter(status='COMPLETED').count(),
        'role': user_role(request.user),
    }
    return render(request, 'dashboard.html', context)


@login_required
def project_list(request):
    projects = Project.objects.all().order_by('-start_date')
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def create_project(request):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can create projects.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})


@login_required
def edit_project(request, pk):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can edit projects.')
        return redirect('project_list')

    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_form.html', {'form': form, 'edit_mode': True, 'project': project})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all().order_by('due_date')
    updates = TaskUpdate.objects.filter(task__project=project).select_related('task', 'updated_by').order_by('-update_time')
    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks,
        'updates': updates,
    })


@login_required
def delete_project(request, pk):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can delete projects.')
        return redirect('project_list')

    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    return render(request, 'confirm_delete.html', {'object': project})


@login_required
def create_task(request):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can create tasks.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {'form': form})


@login_required
def edit_task(request, pk):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can edit tasks.')
        return redirect('dashboard')

    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('project_detail', pk=updated_task.project.pk)
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {'form': form, 'edit_mode': True, 'task': task})


@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by('due_date')
    return render(request, 'my_tasks.html', {'tasks': tasks})


@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.assigned_to != request.user:
        messages.error(request, 'You can only update your own tasks.')
        return redirect('my_tasks')

    if request.method == 'POST':
        task.status = request.POST.get('status')
        task.save()

        TaskUpdate.objects.create(
            task=task,
            updated_by=request.user,
            comment=request.POST.get('comment', 'Status updated'),
            progress_note=request.POST.get('progress_note', 'Task updated')
        )

        messages.success(request, 'Task status updated successfully.')

    return redirect('my_tasks')


@login_required
def field_list(request):
    fields = Field.objects.all().order_by('field_name')
    return render(request, 'field_list.html', {'fields': fields})


@login_required
def create_field(request):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can create fields.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Field created successfully.')
            return redirect('field_list')
    else:
        form = FieldForm()

    return render(request, 'field_form.html', {'form': form})


@login_required
def edit_field(request, pk):
    if user_role(request.user) not in ['OWNER', 'MANAGER']:
        messages.error(request, 'Only owners and managers can edit fields.')
        return redirect('field_list')

    field = get_object_or_404(Field, pk=pk)

    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, 'Field updated successfully.')
            return redirect('field_list')
    else:
        form = FieldForm(instance=field)

    return render(request, 'field_form.html', {'form': form, 'edit_mode': True, 'field': field})