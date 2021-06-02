from django import forms

from .models import Company


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
