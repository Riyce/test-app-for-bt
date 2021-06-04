from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from .models import City, Company, News, User

USERNAME1 = 'Name1'
USERNAME2 = 'Name2'
USERNAME3 = 'Name3'
USERNAME4 = 'Name4'
USERNAME5 = 'Name5'
INDEX = reverse('index')
CREATE = reverse('create')


class AppTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_owner_with_company = User.objects.create_user(
            username=USERNAME1
        )
        cls.user_owner_without_company = User.objects.create_user(
            username=USERNAME2
        )
        cls.user_moderator_with_company = User.objects.create_user(
            username=USERNAME3
        )
        cls.user_moderator_without_company = User.objects.create_user(
            username=USERNAME4
        )
        cls.just_user = User.objects.create_user(username=USERNAME5)
        cls.city = City.objects.create(name='Тестбург', slug='test')
        cls.first_company = Company.objects.create(
            name='ООО "Тестовая компания №1"',
            phone='89997776655',
            email='test@mail.ru',
            discription='Очень длинное и подробное описание первой компании.',
            foundation_date='2010-12-12',
            adress='ул. Тестовая, д. 404',
            city=cls.city,
            owner=cls.user_owner_with_company,
        )
        cls.first_news = News.objects.create(
            title='Первая новость',
            body='Первая новость',
            company=cls.first_company
        )
        cls.user_owner_with_company.profile.company = cls.first_company
        cls.user_owner_with_company.profile.role = 'owner'
        cls.user_owner_without_company.profile.role = 'owner'
        cls.user_moderator_with_company.profile.company = cls.first_company
        cls.user_moderator_with_company.profile.role = 'moderator'
        cls.user_moderator_without_company.profile.role = 'moderator'

        cls.guest_client = Client()
        cls.client_owner_with_company = Client()
        cls.client_owner_without_company = Client()
        cls.client_moderator_with_company = Client()
        cls.client_moderator_without_company = Client()
        cls.just_client = Client()

        cls.client_owner_with_company.force_login(cls.user_owner_with_company)
        cls.client_owner_without_company.force_login(
            cls.user_owner_without_company
        )
        cls.client_moderator_with_company.force_login(
            cls.user_moderator_with_company
        )
        cls.client_moderator_without_company.force_login(
            cls.user_moderator_without_company
        )
        cls.just_client.force_login(cls.just_user)

        cls.COMPANY_PAGE = reverse('company', args=[cls.first_company.pk])
        cls.UPDATE = reverse('update', args=[cls.first_company.pk])
        cls.DELETE = reverse('delete', args=[cls.first_company.pk])
        cls.LEFT_COMPANY = reverse('left', args=[cls.first_company.pk])
        cls.JOIN_COMPANY = reverse('join', args=[cls.first_company.pk])
        cls.CREATE_NEWS = reverse('create_news', args=[cls.first_company.pk])
        cls.SET_MODERATOR_STATUS = reverse(
            'set_moderator', args=[cls.first_company.pk, cls.just_user.pk]
        )
        cls.SET_USER_STATUS = reverse(
            'set_user', args=[
                cls.first_company.pk, cls.user_moderator_with_company.pk
            ]
        )

    def test_status_codes_for_clients(self):
        status_codes = {
            self.guest_client: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 302,
                self.COMPANY_PAGE: 200
            },
            self.client_owner_with_company: {
                INDEX: 200,
                CREATE: 200,
                self.UPDATE: 200,
                self.COMPANY_PAGE: 200
            },
            self.client_moderator_with_company: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 200,
                self.COMPANY_PAGE: 200
            },
            self.just_client: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 302,
                self.COMPANY_PAGE: 200
            },
            self.client_owner_without_company: {
                INDEX: 200,
                CREATE: 200,
                self.UPDATE: 302,
                self.COMPANY_PAGE: 200
            },
            self.client_moderator_without_company: {
                INDEX: 200,
                CREATE: 302,
                self.UPDATE: 302,
                self.COMPANY_PAGE: 200
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
            self.client_moderator_with_company: count_before,
            self.client_moderator_without_company: count_before,
            self.just_client: count_before,
            self.client_owner_without_company: count_before + 1,
            self.client_owner_with_company: count_before + 1,
        }
        for client, companies_count in clients.items():
            with self.subTest():
                client.post(CREATE, data=form_data, follow=True)
                count_after = Company.objects.all().count()
                self.assertEqual(count_after, companies_count)
                try:
                    company = get_object_or_404(Company,
                                                name=form_data['name'])
                    company.delete()
                except Exception:
                    continue

    def test_delete_company(self):
        count_before = Company.objects.all().count()
        self.assertEqual(count_before, 1)
        clients = {
            self.guest_client: count_before,
            self.client_owner_without_company: count_before,
            self.client_moderator_with_company: count_before,
            self.client_moderator_without_company: count_before,
            self.just_client: count_before,
            self.client_owner_with_company: count_before - 1,
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
            self.client_owner_without_company: self.first_company.name,
            self.client_moderator_without_company: self.first_company.name,
            self.just_client: self.first_company.name,
            self.client_moderator_with_company: form_data['name'],
            self.client_owner_with_company: form_data['name'],
        }
        for client, final_name in clients.items():
            with self.subTest():
                client.post(self.UPDATE, data=form_data, follow=True)
                company = Company.objects.get(email=self.first_company.email)
                self.assertEqual(company.name, final_name)
                company.name = self.first_company.name

    def test_join_company(self):
        count_before = self.first_company.staff.count()
        self.assertEqual(count_before, 2)
        self.client_moderator_without_company.get(self.JOIN_COMPANY)
        count_after_1 = self.first_company.staff.count()
        user_moderator_without_company = User.objects.get(username=USERNAME4)
        company_of_user_moderator = (
            user_moderator_without_company.profile.company
        )
        role = user_moderator_without_company.profile.role
        self.assertEqual(count_after_1, count_before + 1)
        self.assertEqual(company_of_user_moderator, self.first_company)
        self.assertEqual(role, 'user')
        self.guest_client.get(self.JOIN_COMPANY)
        count_after_2 = self.first_company.staff.count()
        self.assertEqual(count_after_2, count_before + 1)
        self.just_client.get(self.JOIN_COMPANY)
        count_after_3 = self.first_company.staff.count()
        just_user = User.objects.get(username=USERNAME5)
        company_of_just_user = just_user.profile.company
        self.assertEqual(count_after_3, count_before + 2)
        self.assertEqual(company_of_just_user, self.first_company)

    def test_left_company(self):
        count_before = self.first_company.staff.count()
        self.assertEqual(count_before, 2)
        self.client_owner_with_company.get(self.LEFT_COMPANY)
        count_after1 = self.first_company.staff.count()
        role = self.user_owner_with_company.profile.role
        self.assertEqual(role, 'owner')
        self.assertEqual(count_before-1, count_after1)
        self.client_moderator_with_company.get(self.LEFT_COMPANY)
        count_after2 = self.first_company.staff.count()
        self.assertEqual(count_before-2, count_after2)
        user = User.objects.get(username=USERNAME3)
        company = user.profile.company
        role = user.profile.role
        self.assertFalse(company)
        self.assertEqual(role, 'user')

    def test_create_news(self):
        self.just_client.get(self.JOIN_COMPANY)
        news_count_before = self.first_company.news.all().count()
        self.assertEqual(news_count_before, 1)
        form_data = {
            'title': 'Еще новость',
            'body': 'Еще новость'
        }
        clients = {
            self.guest_client: news_count_before,
            self.client_owner_without_company: news_count_before,
            self.client_moderator_without_company: news_count_before,
            self.just_client: news_count_before,
            self.client_moderator_with_company: news_count_before + 1,
            self.client_owner_with_company: news_count_before + 2,
        }
        for client, news_count in clients.items():
            with self.subTest():
                client.post(self.CREATE_NEWS, data=form_data, follow=True)
                count_after = self.first_company.news.all().count()
                self.assertEqual(count_after, news_count)

    def test_set_moderator_status(self):
        user = User.objects.get(username=USERNAME5)
        self.assertEqual(user.profile.role, 'user')
        self.client_owner_with_company.get(self.SET_MODERATOR_STATUS)
        user_after_first_try = User.objects.get(username=USERNAME5)
        self.assertEqual(user_after_first_try.profile.role, 'user')
        self.just_client.get(self.JOIN_COMPANY)
        self.client_owner_with_company.get(self.SET_MODERATOR_STATUS)
        user_after_second_try = User.objects.get(username=USERNAME5)
        self.assertEqual(user_after_second_try.profile.role, 'moderator')

    def test_set_user_status(self):
        user = User.objects.get(username=USERNAME3)
        self.assertEqual(user.profile.role, 'moderator')
        self.client_owner_with_company.get(self.SET_USER_STATUS)
        user_after_first_try = User.objects.get(username=USERNAME3)
        self.assertEqual(user_after_first_try.profile.role, 'user')
