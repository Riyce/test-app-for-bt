from django import forms
from django.forms.widgets import Textarea

from .models import Company, News


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'phone', 'email', 'discription',
                  'foundation_date', 'adress', 'city')
        labels = {
            'name': ('Название организации'),
            'phone': ('Контактный телефон'),
            'email': ('E-mail'),
            'discription': ('Описание'),
            'foundation_date': ('Дата основани'),
            'adress': ('Адрес'),
            'city': ('Город'),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ('title', 'body')
        labels = {
            'title': ('Заголовок'),
            'body': ('Текст новости'),
        }
        widgets = {'body': Textarea()}
