from django.test import Client, TestCase
from django.urls import reverse

from .models import City, Company, User

USERNAME1 = 'Oleg'
USERNAME2 = 'neOleg'
INDEX = reverse('index')
CREATE = reverse('create')


class AppTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.oleg_user = User.objects.create_user(username=USERNAME1)
        cls.neoleg_user = User.objects.create_user(username=USERNAME2)
        cls.city = City.objects.create(name='Тестбург', slug='test')
        cls.first_company = Company.objects.create(
            name='ООО "Тестовая компания №1"',
            phone='89997776655',
            email='test@mail.ru',
            discription='Очень длинное и подробное описание первой компании.',
            foundation_date='2010-12-12',
            adress='ул. Тестовая, д. 404',
            city=cls.city,
            owner=cls.oleg_user,
        )
        print(cls.first_company.owner)
        cls.oleg_user.profile.company = cls.first_company
        cls.guest_client = Client()
        cls.oleg_client_with_company = Client()
        cls.neoleg_client_without_company = Client()
        cls.oleg_client_with_company.force_login(cls.oleg_user)
        cls.neoleg_client_without_company.force_login(cls.neoleg_user)
        cls.UPDATE = reverse('update', args=[cls.first_company.pk])
        cls.DELETE = reverse('delete', args=[cls.first_company.pk])
        cls.LEFT_COMPANY = reverse('left', args=[cls.first_company.pk])
        cls.JOIN_COMPANY = reverse('join', args=[cls.first_company.pk])

    def test_status_codes_for_clients(self):
        status_codes = {
            self.guest_client: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 302
            },
            self.oleg_client_with_company: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 200
            },
            self.neoleg_client_without_company: {
                INDEX: 200,
                CREATE: 200,
                self.UPDATE: 302
            }
        }
        for client, data in status_codes.items():
            for url, ststus_code in data.items():
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, ststus_code)

    def test_create_company(self):
        count_before = Company.objects.all().count()
        self.assertEqual(count_before, 1)
        form_data = {
            'name': 'ООО "Тестовая компания №2"',
            'phone': '89991112233',
            'email': 'test2@mail.ru',
            'discription': 'Еще одно длинное и подробное описание компании.',
            'foundation_date': '2010-12-12',
            'adress': 'ул. Тестовая, д. 201',
            'city': self.city.pk,
        }
        clients = {
            self.guest_client: count_before,
            self.oleg_client_with_company: count_before,
            self.neoleg_client_without_company: count_before + 1,
        }
        for client, companies_count in clients.items():
            with self.subTest():
                client.post(CREATE, data=form_data, follow=True)
                count_after = Company.objects.all().count()
                self.assertEqual(count_after, companies_count)

    def test_delete_company(self):
        count_before = Company.objects.all().count()
        self.assertEqual(count_before, 1)
        clients = {
            self.guest_client: count_before,
            self.neoleg_client_without_company: count_before,
            self.oleg_client_with_company: count_before - 1,
        }
        for client, companies_count in clients.items():
            with self.subTest():
                client.delete(self.DELETE)
                count_after = Company.objects.all().count()
                self.assertEqual(count_after, companies_count)

    def test_update_company(self):
        form_data = {
            'name': 'ООО "Еще одна тестовая компания №1"',
            'phone': self.first_company.phone,
            'email': self.first_company.email,
            'discription': self.first_company.discription,
            'foundation_date': self.first_company.foundation_date,
            'adress': self.first_company.adress,
            'city': self.city.pk,
        }
        clients = {
            self.guest_client: self.first_company.name,
            self.neoleg_client_without_company: self.first_company.name,
            self.oleg_client_with_company: form_data['name'],
        }
        for client, final_name in clients.items():
            with self.subTest():
                client.post(self.UPDATE, data=form_data, follow=True)
                company = Company.objects.get(email=self.first_company.email)
                self.assertEqual(company.name, final_name)

    def test_join_company(self):
        count_before = self.first_company.staff.count()
        self.assertEqual(count_before, 1)
        self.neoleg_client_without_company.get(self.JOIN_COMPANY)
        first_count_after = self.first_company.staff.count()
        user = User.objects.get(username=USERNAME2)
        company = user.profile.company
        self.assertEqual(first_count_after, count_before + 1)
        self.assertEqual(company, self.first_company)
        self.guest_client.get(self.JOIN_COMPANY)
        second_count_after = self.first_company.staff.count()
        self.assertEqual(second_count_after, count_before + 1)

    def test_left_company(self):
        count_before = self.first_company.staff.count()
        self.assertEqual(count_before, 1)
        self.oleg_client_with_company.get(self.LEFT_COMPANY)
        count_after = self.first_company.staff.count()
        user = User.objects.get(username=USERNAME1)
        company = user.profile.company
        self.assertEqual(count_before - 1, count_after)
        self.assertFalse(company)
