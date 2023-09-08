from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import TextInput

from budget.models import Category, FamilyMember, Income, Family


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter a category name'}),
        }


class FamilyMemberForm(UserCreationForm):
    class Meta:
        model = FamilyMember
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please enter your username'})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please enter your first name'})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please enter your last name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Please enter your email'})

        self.fields['phone_number'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please enter your phone number'})

        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please enter your password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Please re-enter your password'})


class FamilyMemberUpdateForm(forms.ModelForm):

    class Meta:
        model = FamilyMember
        fields = ['first_name', 'last_name', 'email', 'phone_number']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your new first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your new last name'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your new email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your new phone number'}),
        }



class AuthenticationNewForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Please enter your username'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Please enter your password'
        })


class IncomeForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = '__all__'

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your name'}),
            'date_time': TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'value': TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter a decimal value'}),
        }

class FamilyForm(forms.ModelForm):

    class Meta:
        model = Family
        fields = '__all__'


