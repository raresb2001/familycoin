from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, Avg, Q
from django.db.models.functions import ExtractDay
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView, DetailView

from budget.forms import CategoryForm, FamilyMemberForm, IncomeForm, FamilyForm, FamilyMemberUpdateForm
from budget.models import Category, FamilyMember, Income, Family


class HomeTemplateView(TemplateView):
    template_name = 'home/homepage.html'


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        before = int(self.request.GET.get('before', 0))
        current_date = timezone.now().date()
        current_date = current_date - timedelta(days=current_date.weekday())
        current_date_month = timezone.now().date().replace(day=1)

        labels_week = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
        labels_month = get_labels(current_date_month + relativedelta(months=before), relativedelta(months=1))

        chart = generate_bar_chart(labels_week, before, self.request)
        line = generate_line_chart(labels_week, before, self.request)
        line_month = generate_line_chart(labels_month, before, self.request)

        category_order = Income.objects.filter(family_member=self.request.user).values('category__name').annotate(
            total_value=Sum('value')).order_by('-total_value')
        context['category_order'] = category_order

        context['chart'] = chart
        context['line'] = line
        context['line_month'] = line_month

        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'category/create_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('list-category')


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = 'category/list_category.html'
    model = Category
    context_object_name = 'all_category'


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'category/update_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('list-category')


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'category/delete_category.html'
    model = Category
    success_url = reverse_lazy('list-category')


class FamilyMemberCreateView(SuccessMessageMixin, CreateView):
    template_name = 'familymember/create_member.html'
    model = FamilyMember
    form_class = FamilyMemberForm
    success_url = reverse_lazy('login')
    success_message = "The member {t_name} {t_lastname} was created successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message.format(t_name=self.object.first_name, t_lastname=self.object.last_name)


class FamilyMemberListView(LoginRequiredMixin, ListView):
    template_name = 'familymember/list_members.html'
    model = FamilyMember
    context_object_name = 'all_members'

    def get_queryset(self):
        return FamilyMember.objects.all() #Query pentru a obtine toti membrii

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_families'] = Family.objects.all()
        return context  #Query pentru a obtine toate familiile


class FamilyMemberUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'familymember/update_member.html'
    model = FamilyMember
    form_class = FamilyMemberUpdateForm
    success_url = reverse_lazy('list-member')


class FamilyMemberDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'familymember/delete_member.html'
    model = FamilyMember
    success_url = reverse_lazy('list-member')


class IncomeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'income/create_income.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('list-income')


class IncomeListView(LoginRequiredMixin, ListView):
    template_name = 'income/list_income.html'
    model = Income
    context_object_name = 'all_income'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['familymember'] = self.request.user
        return context


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'income/update_income.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('list-income')


class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'income/delete_income.html'
    model = Income
    success_url = reverse_lazy('list-income')


class FamilyCreateView(LoginRequiredMixin, CreateView):
    template_name = 'family/create_family.html'
    model = Family
    form_class = FamilyForm
    success_url = reverse_lazy('list-family')


class FamilyListView(ListView):
    template_name = 'family/list_family.html'
    model = Family
    context_object_name = 'all_family'

    def get_queryset(self):
        return Family.objects.filter(members=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['family_user'] = self.request.user
        return context


class FamilyDeteleView(DeleteView):
    template_name = 'family/delete_family.html'
    model = Family
    success_url = reverse_lazy('list-family')


class FamilyUpdateView(UpdateView):
    template_name = 'family/update_family.html'
    model = Family
    form_class = FamilyForm
    success_url = reverse_lazy('list-family')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        error_message = 'Incorrect username or password. Please try again.'
        return render(self.request, self.template_name, {'error_message': error_message, 'form': form})


def get_labels(start, delta):
    result = []
    now = start
    stop = start + delta
    while now < stop:
        result.append(now)
        now += relativedelta(days=1)
    return result


def get_values(labels, request):
    budget_value = []
    for label in labels:
        budget = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                       date_time__day=label.day, family_member=request.user).aggregate(Sum('value'))[
            'value__sum']
        budget_value.append(float(budget) if budget is not None else 0)
    return budget_value


def get_average_budget(labels, request):
    budget_value = []
    for label in labels:
        budget = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                       date_time__day=label.day, family_member=request.user).aggregate(Avg('value'))[
            'value__avg']
        budget_value.append(float(budget) if budget is not None else 0)
    return budget_value


def generate_bar_chart(labels, before, request):
    budget_value = get_values(labels, request)
    budget_value2 = get_average_budget(labels, request)
    labels = [str(l) for l in labels]
    return {
        'labels': labels,
        'next': min(0, before + 1),
        'previous': before - 1,
        'budget_value': budget_value,
        'budget_value2': budget_value2,
    }


def generate_line_chart(labels, before, request):
    budget_value = get_profit(labels, request)
    budget_value2 = get_rate(labels, request)
    labels = [str(l) for l in labels]
    return {
        'labels': labels,
        'next': min(0, before + 1),
        'previous': before - 1,
        'budget_value': budget_value,
        'budget_value2': budget_value2,
    }


def get_average_category(current_date, request, filter_year=False, filter_month=False, filter_week=False,
                         filter_day=False):
    labels = []
    budget_value = []
    categories = Category.objects.all()
    for category in categories:
        labels.append(category.name)
        query = Q(category=category)
        if filter_year:
            query = query & Q(date_time__year=current_date.year)
        if filter_month:
            query = query & Q(date_time__month=current_date.month)
        if filter_day:
            query = query & Q(date_time__day=current_date.day)
        if filter_week:
            dt_from = current_date.replace(day=current_date.day - current_date.weekday())
            dt_to = dt_from + relativedelta(weeks=1)
            query = query & Q(date_time__lte=dt_to, date_time__gte=dt_from)
        budget = Income.objects.filter(query, family_member=request.user).aggregate(Avg('value'))['value__avg']
        budget_value.append(float(budget) if budget is not None else 0)
    return labels, budget_value


def get_profit(labels, request):
    budget_value = []
    for label in labels:
        budget_income = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                              date_time__day=label.day, family_member=request.user,
                                              type='income').aggregate(Sum('value'))['value__sum']
        budget_expense = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                               date_time__day=label.day, family_member=request.user,
                                               type='expense').aggregate(Sum('value'))['value__sum']
        budget_income = budget_income if budget_income is not None else 0
        budget_expense = budget_expense if budget_expense is not None else 0
        budget = budget_income - budget_expense
        budget_value.append(float(budget) if budget is not None else 0)
    return budget_value


def get_rate(labels, request):
    budget_value = []
    for label in labels:
        budget_income = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                              date_time__day=label.day, family_member=request.user,
                                              type='income').aggregate(Sum('value'))['value__sum']
        budget_expense = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                               date_time__day=label.day, family_member=request.user,
                                               type='expense').aggregate(Sum('value'))['value__sum']
        budget_income = budget_income if budget_income is not None else 0
        budget_expense = budget_expense if budget_expense is not None else 0
        economics = budget_income - budget_expense
        if budget_income == 0:
            rate = 0
        else:
            rate = (economics / budget_income) * 100
        budget_value.append(float(rate) if rate is not None else 0)
    return budget_value


@login_required
def years_chart_view(request):
    context_year = {}
    before = int(request.GET.get('before', 0))

    start = timezone.now().date().replace(month=1, day=1)
    labels_year = get_labels(start + relativedelta(years=before), relativedelta(years=1))

    budget_value = get_values(labels_year, request)
    labels_year = [str(l) for l in labels_year]
    context_year['labels_year'] = labels_year
    context_year['next'] = min(0, before + 1)
    context_year['previous'] = before - 1
    context_year['budget_value'] = budget_value

    return render(request, 'dashboard/year.html', context_year)


@login_required
def months_chart_view(request):
    context = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date().replace(day=1)
    labels = get_labels(current_date + relativedelta(months=before), relativedelta(months=1))
    budget_value = get_values(labels, request)
    labels = [str(l) for l in labels]

    context['labels'] = labels
    context['next'] = min(0, before + 1)
    context['previous'] = before - 1
    context['budget_value'] = budget_value
    return render(request, 'dashboard/month.html', context)


@login_required
def week_chart_view(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())

    labels_week = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    chart = generate_bar_chart(labels_week, before, request)
    context_week['chart'] = chart
    return render(request, 'dashboard/week.html', context_week)


@login_required
def daily_chart_view(request):
    context_day = {}
    labels_day = []

    current_date1 = timezone.now().date()
    labels_day.append(current_date1)

    budget_value = get_values(labels_day, request)

    labels_day = [str(l) for l in labels_day]
    context_day['labels_day'] = labels_day
    context_day['budget_value'] = budget_value

    return render(request, 'dashboard/day.html', context_day)


def get_values_category(current_date, request, filter_year=False, filter_month=False, filter_week=False,
                        filter_day=False):
    labels = []
    budget_value = []
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    categories = Category.objects.all()
    for category in categories:
        labels.append(category.name)
        query = Q(category=category)
        if filter_year:
            query = query & Q(date_time__year=current_date.year)
        if filter_month:
            query = query & Q(date_time__month=current_date.month)
        if filter_day:
            query = query & Q(date_time__day=current_date.day)
        if filter_week:
            dt_from = current_date.replace(day=current_date.day - current_date.weekday())
            dt_to = dt_from + relativedelta(weeks=1)
            query = query & Q(date_time__gte=dt_from, date_time__lte=dt_to)
        budget = Income.objects.filter(query, family_member=request.user).aggregate(Sum('value'))['value__sum']
        budget_value.append(float(budget) if budget is not None else 0)
    return labels, budget_value


@login_required
def category_year_view(request):
    context_year = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now() + relativedelta(years=before)
    labels, budget_value = get_values_category(current_date, request, filter_year=True)

    labels_year = [str(l) for l in labels]
    context_year['labels_year'] = labels_year
    context_year['next'] = min(0, before + 1)
    context_year['previous'] = before - 1
    context_year['budget_value'] = budget_value
    return render(request, 'dashboard/year_category.html', context_year)


@login_required
def category_month_view(request):
    context_month = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now() + relativedelta(months=before)
    labels, budget_value = get_values_category(current_date, request, filter_year=True, filter_month=True)

    labels_month = [str(l) for l in labels]
    context_month['labels_month'] = labels_month
    context_month['next'] = min(0, before + 1)
    context_month['previous'] = before - 1
    context_month['budget_value'] = budget_value
    return render(request, 'dashboard/month_category.html', context_month)


@login_required
def category_week_view(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now() + relativedelta(weeks=before)
    labels, budget_value = get_values_category(current_date, request, filter_year=True,
                                               filter_week=True)
    labels_week = [str(l) for l in labels]
    context_week['labels_week'] = labels_week
    context_week['next'] = min(0, before + 1)
    context_week['previous'] = before - 1
    context_week['budget_value'] = budget_value
    return render(request, 'dashboard/week_category.html', context_week)


@login_required
def category_day_view(request):
    context_day = {}
    labels_day = []

    current_date2 = timezone.now().date()

    budget_value = []
    categories = Category.objects.filter()

    for category in categories:
        labels_day.append(category.name)

        budget = Income.objects.filter(date_time__day=current_date2.day, category=category).aggregate(Sum('value'))[
            'value__sum']
        budget_value.append(float(budget) if budget is not None else 0)

    labels_day = [str(l) for l in labels_day]
    context_day['labels_day'] = labels_day
    context_day['budget_value'] = budget_value

    return render(request, 'dashboard/day_category.html', context_day)


@login_required
def week_average_view(request):
    context_week_average = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())
    labels_week_average = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    budget_value = get_average_budget(labels_week_average, request)
    labels_week_average = [str(l) for l in labels_week_average]

    context_week_average['labels_week_average'] = labels_week_average
    context_week_average['next'] = min(0, before + 1)
    context_week_average['previous'] = before - 1
    context_week_average['budget_value'] = budget_value
    return render(request, 'dashboard/week_average.html', context_week_average)


@login_required
def week_profit_view(request):
    context_week_profit = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())
    labels_week_profit = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    budget_value = get_profit(labels_week_profit, request)
    labels_week_profit = [str(l) for l in labels_week_profit]

    context_week_profit['labels_week_profit'] = labels_week_profit
    context_week_profit['next'] = min(0, before + 1)
    context_week_profit['previous'] = before - 1
    context_week_profit['budget_value'] = budget_value
    return render(request, 'dashboard/week_profit.html', context_week_profit)


@login_required
def month_economic_rate_view(request):
    context_rate = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date().replace(day=1)
    labels_economic = get_labels(current_date + relativedelta(months=before), relativedelta(months=1))
    budget_value = get_rate(labels_economic, request)
    labels_economic = [str(l) for l in labels_economic]

    context_rate['labels_economic'] = labels_economic
    context_rate['next'] = min(0, before + 1)
    context_rate['previous'] = before - 1
    context_rate['budget_value'] = budget_value
    return render(request, 'dashboard/month_economic_rate.html', context_rate)


@login_required
def week_category_average(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now() + relativedelta(weeks=before)
    labels, budget_value = get_values_category(current_date, request, filter_year=True, filter_month=True,
                                               filter_week=True)

    labels_week = [str(l) for l in labels]
    context_week['labels_week'] = labels_week
    context_week['next'] = min(0, before + 1)
    context_week['previous'] = before - 1
    context_week['budget_value'] = budget_value
    return render(request, 'dashboard/week_category_average.html', context_week)


class FamilyDetailView(DetailView):
    template_name = 'family/detail_family.html'
    model = Family
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate monthly expenses
        total_expenses = self.calculate_monthly_expenses(self.request.user)

        context['total_expenses'] = total_expenses
        return context

    def calculate_monthly_expenses(self, user):
        current_date = datetime.now()
        monthly_incomes = Income.objects.filter(
            date_time__year=current_date.year,
            date_time__month=current_date.month,
            family_member=user
        )
        total_expenses = monthly_incomes.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
        return total_expenses


def family_monthly_expenses(request):
    current_date = datetime.now()
    monthly_incomes = Income.objects.filter(
        date_time__year=current_date.year,
        date_time__month=current_date.month,
        family_member=request.user
    )

    total_expenses = monthly_incomes.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0

    return render(request, 'dashboard/monthly_expenses.html', {'total_expenses': total_expenses})


