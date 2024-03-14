from functools import reduce

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class FamilyMember(AbstractUser):
    SOURCE_TYPE = (
        ('Kid', 'Kid'),
        ('Parent', 'Parent'),
        ('Grandparent', 'Grandparent'),
    )

    phone_number = models.CharField(max_length=25)
    type = models.CharField(max_length=32, choices=SOURCE_TYPE, default='Parent')
    age = models.IntegerField(null=True, blank=True)



class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Income(models.Model):
    SOURCE_TYPE = (
        ('income', 'Income'),  # income apare in baza de date si Income  apare pe dropdown la user
        ('expense', 'Expense'),
    )

    name = models.CharField(max_length=20)
    date_time = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True) #specifică că atunci când o categorie este ștearsă, obiectele asociate din clasa curentă vor fi, de asemenea, șterse, iar null=True permite ca acest câmp să fie lăsat gol.
    value = models.DecimalField(max_digits=10, decimal_places=2)
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=32, choices=SOURCE_TYPE)

    def __str__(self):
        return f'{self.name}'


class Family(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='owner')
    members = models.ManyToManyField(FamilyMember, blank=True, related_name='members')

    def __str__(self):
        return f'{self.name}'

    def members_str(self):
        # return reduce(lambda first, second: f'{first}, {second.first_name}', self.members.all(), f'')[2:]
        return f'{", ".join([member.first_name for member in self.members.all()])}'


#sa sterg clasas membership si sa afisez doar membrul curent si informatii despre el