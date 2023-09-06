from datetime import timedelta, datetime


from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Avg, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView

from budget.forms import CategoryForm, FamilyMemberForm, IncomeForm
from budget.models import Category, FamilyMember, Income


class HomeTemplateView(TemplateView):
    template_name = 'homepage.html'

class DashboardTemplateView(TemplateView):
    template_name = 'dashboard/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        before = int(self.request.GET.get('before', 0))
        current_date = timezone.now().date()
        current_date = current_date - timedelta(days=current_date.weekday())
        current_date_month = timezone.now().date().replace(day=1)


        labels_week = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
        labels_month = get_labels(current_date_month + relativedelta(months=before), relativedelta(months=1))

        chart = generate_bar_chart(labels_week, before)
        line = generate_line_chart(labels_week, before)
        line_month = generate_line_chart(labels_month, before)

        category_order = Income.objects.values('category__name').annotate(total_value=Sum('value')).order_by('-total_value')
        context['category_order'] = category_order

        context['chart'] = chart
        context['line'] = line
        context['line_month'] = line_month

        return context


class CategoryCreateView(CreateView):
    template_name = 'category/create_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('list-category')


class CategoryListView(ListView):
    template_name = 'category/list_category.html'
    model = Category
    context_object_name = 'all_category'


class CategoryUpdateView(UpdateView):
    template_name = 'category/update_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('list-category')


class CategoryDeleteView(DeleteView):
    template_name = 'category/delete_category.html'
    model = Category
    success_url = reverse_lazy('list-category')


class FamilyMemberCreateView(CreateView):
    template_name = 'familymember/create_member.html'
    model = FamilyMember
    form_class = FamilyMemberForm
    success_url = reverse_lazy('login')


class FamilyMemberListView(ListView):
    template_name = 'familymember/list_members.html'
    model = FamilyMember
    context_object_name = 'all_members'


class FamilyMemberUpdateView(UpdateView):
    template_name = 'familymember/update_member.html'
    model = FamilyMember
    form_class = FamilyMemberForm
    success_url = reverse_lazy('list-member')


class FamilyMemberDeleteView(DeleteView):
    template_name = 'familymember/delete_member.html'
    model = FamilyMember
    success_url = reverse_lazy('list-member')


class IncomeCreateView(CreateView):
    template_name = 'income/create_income.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('list-income')


class IncomeListView(ListView):
    template_name = 'income/list_income.html'
    model = Income
    context_object_name = 'all_income'


class IncomeUpdateView(UpdateView):
    template_name = 'income/update_income.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('list-income')


class IncomeDeleteView(DeleteView):
    template_name = 'income/delete_income.html'
    model = Income
    success_url = reverse_lazy('list-income')


def get_labels(start, delta):
    result = []
    now = start
    stop = start + delta
    # print(f'generating from start={start} until stop={stop}')
    while now < stop:
        # print(f'adding {now}, next is {now + relativedelta(days=1)}')
        result.append(now)
        now += relativedelta(days=1)
    return result


def get_values(labels):
    budget_value = []
    for label in labels:
        budget = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                       date_time__day=label.day).aggregate(Sum('value'))['value__sum']
        budget_value.append(float(budget) if budget is not None else 0)
    return budget_value

def generate_bar_chart(labels, before):
    budget_value = get_values(labels)
    budget_value2 = get_average(labels)
    labels = [str(l) for l in labels]
    return {
        'labels': labels,
        'next': min(0, before + 1),
        'previous': before - 1,
        'budget_value': budget_value,
        'budget_value2': budget_value2,
    }


def generate_line_chart(labels, before):
    budget_value = get_profit(labels)
    budget_value2 = get_rate(labels)
    labels = [str(l) for l in labels]
    return {
        'labels': labels,
        'next': min(0, before + 1),
        'previous': before - 1,
        'budget_value': budget_value,
        'budget_value2': budget_value2,
    }


def get_average(current_date, filter_year=False, filter_month=False, filter_day=False):
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

        budget = Income.objects.filter(query).aggregate(Avg('value'))['value__avg']
        budget_value.append(float(budget) if budget is not None else 0)
    return labels, budget_value

def get_profit(labels):
    budget_value = []
    for label in labels:
        budget_income = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                              date_time__day=label.day, type='income').aggregate(Sum('value'))[
            'value__sum']
        budget_expense = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                               date_time__day=label.day, type='expense').aggregate(Sum('value'))[
            'value__sum']
        budget_income = budget_income if budget_income is not None else 0
        budget_expense = budget_expense if budget_expense is not None else 0
        budget = budget_income - budget_expense
        budget_value.append(float(budget) if budget is not None else 0)
    return budget_value


def get_rate(labels):
    budget_value = []
    for label in labels:
        budget_income = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                              date_time__day=label.day, type='income').aggregate(Sum('value'))[
            'value__sum']
        budget_expense = Income.objects.filter(date_time__year=label.year, date_time__month=label.month,
                                               date_time__day=label.day, type='expense').aggregate(Sum('value'))[
            'value__sum']
        budget_income = budget_income if budget_income is not None else 0
        budget_expense = budget_expense if budget_expense is not None else 0
        economics = budget_income - budget_expense
        if budget_income == 0:
            rate = 0
        else:
            rate = (economics / budget_income) * 100
        budget_value.append(float(rate) if rate is not None else 0)
    return budget_value


def years_chart_view(request):
    context_year = {}
    before = int(request.GET.get('before', 0))

    start = timezone.now().date().replace(month=1, day=1)
    labels_year = get_labels(start + relativedelta(years=before), relativedelta(years=1))

    budget_value = get_values(labels_year)
    labels_year = [str(l) for l in labels_year]
    context_year['labels_year'] = labels_year
    context_year['next'] = min(0, before + 1)
    context_year['previous'] = before - 1
    context_year['budget_value'] = budget_value

    return render(request, 'dashboard/year.html', context_year)


def months_chart_view(request):
    context = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date().replace(day=1)
    labels = get_labels(current_date + relativedelta(months=before), relativedelta(months=1))
    budget_value = get_values(labels)
    labels = [str(l) for l in labels]

    context['labels'] = labels
    context['next'] = min(0, before + 1)
    context['previous'] = before - 1
    context['budget_value'] = budget_value
    return render(request, 'dashboard/month.html', context)


def week_chart_view(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())

    labels_week = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    chart = generate_bar_chart(labels_week, before)
    context_week['chart'] = chart
    return render(request, 'dashboard/week.html', context_week)


def daily_chart_view(request):
    context_day = {}
    labels_day = []

    current_date1 = timezone.now().date()
    labels_day.append(current_date1)

    budget_value = get_values(labels_day)

    labels_day = [str(l) for l in labels_day]
    context_day['labels_day'] = labels_day
    context_day['budget_value'] = budget_value

    return render(request, 'dashboard/day.html', context_day)


# de adaugat 3 parametrii si 3 if-uri pentru a diferentia (year, month, week)
def get_values_category(current_date, filter_year=False, filter_month=False, filter_week=False,filter_day=False):
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
            dt_from = current_date.replace(day=current_date.day-current_date.weekday())
            dt_to = dt_from + relativedelta(weeks=1)
            query = query & Q(date_time__lte=dt_to, date_time__gte=dt_from)
        budget = Income.objects.filter(query, ).aggregate(Sum('value'))['value__sum']
        budget_value.append(float(budget) if budget is not None else 0)
    return labels, budget_value


def category_year_view(request):
    context_year = {}
    before = int(request.GET.get('before', 0))

    current_date = datetime.now() + relativedelta(years=before)
    labels, budget_value = get_values_category(current_date, filter_year=True)

    labels_year = [str(l) for l in labels]
    context_year['labels_year'] = labels_year
    context_year['next'] = min(0, before + 1)
    context_year['previous'] = before - 1
    context_year['budget_value'] = budget_value
    return render(request, 'dashboard/year_category.html', context_year)


def category_month_view(request):
    context_month = {}
    before = int(request.GET.get('before', 0))

    current_date = datetime.now() + relativedelta(months=before)
    labels, budget_value = get_values_category(current_date, filter_year=True, filter_month=True)

    labels_month = [str(l) for l in labels]
    context_month['labels_month'] = labels_month
    context_month['next'] = min(0, before + 1)
    context_month['previous'] = before - 1
    context_month['budget_value'] = budget_value
    return render(request, 'dashboard/month_category.html', context_month)


def category_week_view(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = datetime.now() + relativedelta(weeks=before)
    labels, budget_value = get_values_category(current_date, filter_year=True, filter_month=True, filter_week=True)

    labels_week = [str(l) for l in labels]
    context_week['labels_week'] = labels_week
    context_week['next'] = min(0, before + 1)
    context_week['previous'] = before - 1
    context_week['budget_value'] = budget_value
    return render(request, 'dashboard/week_category.html', context_week)


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


def week_average_view(request):
    context_week_average = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())
    labels_week_average = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    budget_value = get_average(labels_week_average)
    labels_week_average = [str(l) for l in labels_week_average]

    context_week_average['labels_week_average'] = labels_week_average
    context_week_average['next'] = min(0, before + 1)
    context_week_average['previous'] = before - 1
    context_week_average['budget_value'] = budget_value
    return render(request, 'dashboard/week_average.html', context_week_average)


def week_profit_view(request):
    context_week_profit = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date()
    current_date = current_date - timedelta(days=current_date.weekday())
    labels_week_profit = get_labels(current_date + relativedelta(weeks=before), relativedelta(weeks=1))
    budget_value = get_profit(labels_week_profit)
    labels_week_profit = [str(l) for l in labels_week_profit]

    context_week_profit['labels_week_profit'] = labels_week_profit
    context_week_profit['next'] = min(0, before + 1)
    context_week_profit['previous'] = before - 1
    context_week_profit['budget_value'] = budget_value
    return render(request, 'dashboard/week_profit.html', context_week_profit)


def month_economic_rate_view(request):
    context_rate = {}
    before = int(request.GET.get('before', 0))

    current_date = timezone.now().date().replace(day=1)
    labels_economic = get_labels(current_date + relativedelta(months=before), relativedelta(months=1))
    budget_value = get_rate(labels_economic)
    labels_economic = [str(l) for l in labels_economic]

    context_rate['labels_economic'] = labels_economic
    context_rate['next'] = min(0, before + 1)
    context_rate['previous'] = before - 1
    context_rate['budget_value'] = budget_value
    return render(request, 'dashboard/month_economic_rate.html', context_rate)


def week_category_average(request):
    context_week = {}
    before = int(request.GET.get('before', 0))

    current_date = datetime.now() + relativedelta(weeks=before)
    labels, budget_value = get_values_category(current_date, filter_year=True, filter_month=True, filter_week=True)

    labels_week = [str(l) for l in labels]
    context_week['labels_week'] = labels_week
    context_week['next'] = min(0, before + 1)
    context_week['previous'] = before - 1
    context_week['budget_value'] = budget_value
    return render(request, 'dashboard/week_category_average.html', context_week)

