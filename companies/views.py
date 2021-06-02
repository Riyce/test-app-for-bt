from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompanyForm
from .models import Company


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
    return render(request, 'company.html', {'company': company})


@login_required
def join_an_organization(request, id):
    if request.user.profile.company is not None:
        return redirect('company', id=id)
    company = get_object_or_404(Company, id=id)
    request.user.profile.company = company
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
    request.user.profile.save()
    return redirect('company', id=id)


@login_required
def create_an_organization(request):
    if request.user.profile.company is not None:
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
    if request.user != company.owner:
        return redirect('company', id=id)
    form = CompanyForm(request.POST or None, instance=company)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'company': company})
    form.save()
    return redirect('company', id=id)
