from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from Salesmanager.models import Drug, Inventory, Sale

User = get_user_model()

# Limit role choices to only SYSTEM_ADMIN and SALES_MANAGER
LIMITED_ROLE_CHOICES = [
    ('SYSTEM_ADMIN', 'System Admin'),
    ('SALES_MANAGER', 'Sales Manager'),
]

class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    role = forms.ChoiceField(choices=LIMITED_ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=LIMITED_ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active', 'is_staff')
        widgets = {
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
        }

class PasswordResetForm(SetPasswordForm):
    """Form for admin to reset user password"""
    class Meta:
        fields = ('new_password1', 'new_password2')

class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ('name', 'description', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ('drug', 'quantity', 'reorder_level')

class DrugInventoryForm(forms.ModelForm):
    """Combined form for creating drug and inventory together"""
    name = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    quantity = forms.IntegerField(required=True, initial=0)
    reorder_level = forms.IntegerField(required=True, initial=10)
    
    class Meta:
        model = Drug
        fields = ('name', 'description', 'price')

