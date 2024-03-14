from django.contrib import admin

from budget.models import FamilyMember, Category, Income, Family

# Register your models here.

admin.site.register(FamilyMember)
admin.site.register(Category)
admin.site.register(Income)
admin.site.register(Family)
