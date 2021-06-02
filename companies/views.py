from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompanyForm, NewsForm
from .models import Company, User


def index(request):
    list = Company.objects.all()
    paginator = Paginator(list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def company(request, id):
    company = get_object_or_404(Company, id=id)
    news = company.news.all()
    form = NewsForm(request.POST or None)
    return render(request, 'company.html', {
        'company': company, 'news': news, 'form': form
    })


@login_required
def join_an_organization(request, id):
    if request.user.profile.company or request.user.profile.role == 'owner':
        return redirect('company', id=id)
    company = get_object_or_404(Company, id=id)
    request.user.profile.company = company
    request.user.profile.role = 'user'
    request.user.profile.save()
    return redirect('company', id=id)


@login_required
def left_an_organization(request, id):
    company = get_object_or_404(Company, id=id)
    if (
        request.user.profile.company != company or
        company.owner == request.user
    ):
        return redirect('company', id=id)
    request.user.profile.company = None
    request.user.profile.role = 'user'
    request.user.profile.save()
    return redirect('company', id=id)


@login_required
def create_an_organization(request):
    if request.user.profile.company or request.user.profile.role != 'owner':
        return redirect('index')
    form = CompanyForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    company = form.save(commit=False)
    company.owner = request.user
    company.save()
    request.user.profile.company = company
    request.user.profile.save()
    return redirect('index')


@login_required
def delete_an_organization(request, id):
    company = get_object_or_404(Company, id=id)
    if request.user == company.owner:
        company.delete()
        return redirect('index')
    return redirect('company', id=id)


@login_required
def update_an_organization(request, id):
    company = get_object_or_404(Company, id=id)
    if not (
        request.user.profile.is_staff and
        request.user.profile.company == company
    ):
        return redirect('company', id=id)
    form = CompanyForm(request.POST or None, instance=company)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'company': company})
    form.save()
    return redirect('company', id=id)


@login_required
def create_news(request, id):
    company = get_object_or_404(Company, id=id)
    if not (
        request.user.profile.company == company and
        request.user.profile.is_staff
    ):
        return redirect('company', id=id)
    form = NewsForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'includes/news.html', {'form': form})
    news = form.save(commit=False)
    news.company = company
    news.save()
    return redirect('company', id=id)


@login_required
def staff_page(request, id):
    company = get_object_or_404(Company, id=id)
    staff = company.staff.all()
    if request.user == company.owner:
        return render(request, 'users.html', {
            'staff': staff, 'company': company
        })
    return redirect('company', id=id)


@login_required
def set_moderator_status(request, id, user_id):
    company = get_object_or_404(Company, id=id)
    if request.user != company.owner:
        return redirect('company', id=id)
    user = get_object_or_404(User, id=user_id)
    if user.profile.company != company:
        return redirect('staff', id=id)
    user.profile.role = 'moderator'
    user.profile.save()
    return redirect('staff', id=id)


@login_required
def set_user_status(request, id, user_id):
    company = get_object_or_404(Company, id=id)
    if request.user != company.owner:
        return redirect('company', id=id)
    user = get_object_or_404(User, id=user_id)
    user.profile.role = 'user'
    user.profile.save()
    return redirect('staff', id=id)
