from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from cooperatives.models import Cooperative

class CooperativeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superadmin = User.objects.create_superuser(
            username='superadmin',
            email='super@admin.com',
            password='password123',
            role='superadmin'
        )
        self.coop1 = Cooperative.objects.create(
            name='Test Cooperative 1',
            code='TC1',
            address='Address 1',
            contact='1234567890'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='password123',
            role='admin',
            cooperative=self.coop1
        )

    def test_superadmin_can_list_cooperatives(self):
        self.client.login(username='superadmin', password='password123')
        response = self.client.get(reverse('cooperatives:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Cooperative 1')

    def test_admin_cannot_list_cooperatives(self):
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('cooperatives:list'))
        self.assertEqual(response.status_code, 403)  # PermissionDenied

    def test_superadmin_can_create_cooperative(self):
        self.client.login(username='superadmin', password='password123')
        data = {
            'name': 'New Cooperative',
            'code': 'NC1',
            'address': 'New Address',
            'contact': '9876543210',
            'status': 'active'
        }
        response = self.client.post(reverse('cooperatives:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cooperative.objects.filter(code='NC1').exists())

    def test_admin_can_view_own_cooperative_detail(self):
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('cooperatives:detail', args=[self.coop1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Cooperative 1')

    def test_admin_cannot_view_other_cooperative_detail(self):
        coop2 = Cooperative.objects.create(name='Other', code='OT1', address='...', contact='...')
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('cooperatives:detail', args=[coop2.pk]))
        self.assertEqual(response.status_code, 404) # CooperativeAccessMixin filters queryset
