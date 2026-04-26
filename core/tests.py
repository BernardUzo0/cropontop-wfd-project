import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, Farm, Field, Project, Task, TaskUpdate


class CropOnTopTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner1', password='password')
        self.manager = User.objects.create_user(username='manager1', password='password')
        self.worker1 = User.objects.create_user(username='worker1', password='password')
        self.worker2 = User.objects.create_user(username='worker2', password='password')

        UserProfile.objects.create(user=self.owner, role='OWNER', full_name='Owner One')
        UserProfile.objects.create(user=self.manager, role='MANAGER', full_name='Manager One')
        UserProfile.objects.create(user=self.worker1, role='WORKER', full_name='Worker One')
        UserProfile.objects.create(user=self.worker2, role='WORKER', full_name='Worker Two')

        self.farm = Farm.objects.create(
            farm_name='Green Valley Farm',
            location='Dublin',
            size_acres=50.00,
            owner=self.owner
        )

        self.field = Field.objects.create(
            field_name='North Field',
            farm=self.farm,
            crop_type='Wheat',
            area_size=20.00
        )

        self.project = Project.objects.create(
            project_name='Spring Wheat Planting',
            description='Planting the spring wheat crop.',
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=14),
            status='ACTIVE',
            farm=self.farm,
            field=self.field,
            created_by=self.manager
        )

        self.task = Task.objects.create(
            title='Prepare Soil',
            description='Prepare the soil for seeding.',
            due_date=datetime.date.today() + datetime.timedelta(days=2),
            priority='HIGH',
            status='PENDING',
            project=self.project,
            assigned_to=self.worker1,
            created_by=self.manager
        )

    def test_project_created(self):
        self.assertEqual(self.project.project_name, 'Spring Wheat Planting')

    def test_task_created(self):
        self.assertEqual(self.task.title, 'Prepare Soil')
        self.assertEqual(self.task.assigned_to.username, 'worker1')

    def test_project_completion_percentage(self):
        Task.objects.create(
            title='Seed Field',
            description='Seed the field.',
            due_date=datetime.date.today(),
            priority='MEDIUM',
            status='COMPLETED',
            project=self.project,
            assigned_to=self.worker1,
            created_by=self.manager
        )
        self.task.status = 'COMPLETED'
        self.task.save()
        self.assertEqual(self.project.completion_percentage(), 100)

    def test_manager_can_edit_project(self):
        self.client.login(username='manager1', password='password')
        response = self.client.post(reverse('edit_project', args=[self.project.pk]), {
            'project_name': 'Updated Project Name',
            'description': 'Updated description',
            'start_date': self.project.start_date,
            'end_date': self.project.end_date,
            'status': 'COMPLETED',
            'farm': self.farm.pk,
            'field': self.field.pk,
        })
        self.project.refresh_from_db()
        self.assertRedirects(response, reverse('project_detail', args=[self.project.pk]))
        self.assertEqual(self.project.project_name, 'Updated Project Name')
        self.assertEqual(self.project.status, 'COMPLETED')

    def test_manager_can_edit_task(self):
        self.client.login(username='manager1', password='password')
        response = self.client.post(reverse('edit_task', args=[self.task.pk]), {
            'title': 'Updated Task',
            'description': 'Updated task description',
            'due_date': self.task.due_date,
            'priority': 'MEDIUM',
            'status': 'IN_PROGRESS',
            'project': self.project.pk,
            'assigned_to': self.worker2.pk,
        })
        self.task.refresh_from_db()
        self.assertRedirects(response, reverse('project_detail', args=[self.project.pk]))
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.assigned_to, self.worker2)

    def test_manager_can_edit_field(self):
        self.client.login(username='manager1', password='password')
        response = self.client.post(reverse('edit_field', args=[self.field.pk]), {
            'field_name': 'Updated Field',
            'farm': self.farm.pk,
            'crop_type': 'Barley',
            'area_size': '22.50',
        })
        self.field.refresh_from_db()
        self.assertRedirects(response, reverse('field_list'))
        self.assertEqual(self.field.field_name, 'Updated Field')
        self.assertEqual(self.field.crop_type, 'Barley')

    def test_worker_cannot_create_project(self):
        self.client.login(username='worker1', password='password')
        response = self.client.get(reverse('create_project'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_worker_cannot_edit_project(self):
        self.client.login(username='worker1', password='password')
        response = self.client.get(reverse('edit_project', args=[self.project.pk]))
        self.assertRedirects(response, reverse('project_list'))

    def test_worker_cannot_create_field(self):
        self.client.login(username='worker1', password='password')
        response = self.client.get(reverse('create_field'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_worker_cannot_edit_field(self):
        self.client.login(username='worker1', password='password')
        response = self.client.get(reverse('edit_field', args=[self.field.pk]))
        self.assertRedirects(response, reverse('field_list'))

    def test_worker_can_update_own_task(self):
        self.client.login(username='worker1', password='password')
        response = self.client.post(reverse('update_task_status', args=[self.task.pk]), {
            'status': 'COMPLETED',
            'progress_note': 'Finished task',
            'comment': 'Completed successfully',
        })
        self.task.refresh_from_db()
        self.assertRedirects(response, reverse('my_tasks'))
        self.assertEqual(self.task.status, 'COMPLETED')
        self.assertEqual(TaskUpdate.objects.count(), 1)

    def test_worker_cannot_update_someone_elses_task(self):
        self.client.login(username='worker2', password='password')
        response = self.client.post(reverse('update_task_status', args=[self.task.pk]), {
            'status': 'COMPLETED',
            'progress_note': 'Trying update',
            'comment': 'Should not work',
        })
        self.task.refresh_from_db()
        self.assertRedirects(response, reverse('my_tasks'))
        self.assertEqual(self.task.status, 'PENDING')
        self.assertEqual(TaskUpdate.objects.count(), 0)