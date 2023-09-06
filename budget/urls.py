from django.urls import path

from budget import views

urlpatterns = [
    path('', views.HomeTemplateView.as_view(), name='homepage'),
    path('dashboard/', views.DashboardTemplateView.as_view(), name='dashboard'),
    path('create_category/', views.CategoryCreateView.as_view(), name='create-category'),
    path('list_category/', views.CategoryListView.as_view(), name='list-category'),
    path('delete_catgory/<int:pk>/', views.CategoryDeleteView.as_view(), name='delete-category'),
    path('update_catgory/<int:pk>/', views.CategoryUpdateView.as_view(), name='update-category'),
    path('create_member/', views.FamilyMemberCreateView.as_view(), name='create-member'),
    path('list_member/', views.FamilyMemberListView.as_view(), name='list-member'),
    path('update_member/<int:pk>/', views.FamilyMemberUpdateView.as_view(), name='update-member'),
    path('delete_member/<int:pk>/', views.FamilyMemberDeleteView.as_view(), name='delete-member'),
    path('create_income/', views.IncomeCreateView.as_view(), name='create-income'),
    path('list_income/', views.IncomeListView.as_view(), name='list-income'),
    path('update_income/<int:pk>/', views.IncomeUpdateView.as_view(), name='update-income'),
    path('delete_income/<int:pk>/', views.IncomeDeleteView.as_view(), name='delete-income'),
    path('year/', views.years_chart_view, name='year'),
    path('month/', views.months_chart_view, name='month'),
    path('week/', views.week_chart_view, name='week'),
    path('day/', views.daily_chart_view, name='day'),
    path('day_category/', views.category_day_view, name='day-category'),
    path('month_category/', views.category_month_view, name='month-category'),
    path('year_category/', views.category_year_view, name='year-category'),
    path('week_category/', views.category_week_view, name='week-category'),
    path('week_average/', views.week_average_view, name='week-average'),
    path('week_profit/', views.week_profit_view, name='week-profit'),
    path('month_economic_rate/', views.month_economic_rate_view, name='month-econrate'),
    path('week_category_average/', views.week_category_average, name='week-category-average'),
]
