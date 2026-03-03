from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import json
from django.db.models import F
from Salesmanager.models import Sale, Drug, Inventory, SalesReport
from .forms import UserCreateForm, UserEditForm, DrugForm, InventoryForm, DrugInventoryForm, PasswordResetForm, PasswordResetForm

# Create your views here.

@login_required
def admin_dashboard(request):
    # Check if user is a system admin
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")

    User = get_user_model()

    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    # Sales statistics
    total_sales_amount = Sale.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Get sales from last 30 days for comparison
    thirty_days_ago = timezone.now() - timedelta(days=30)
    last_month_sales = Sale.objects.filter(
        status='completed',
        date__lt=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate percentage change
    if last_month_sales > 0:
        sales_percentage = ((total_sales_amount - last_month_sales) / last_month_sales) * 100
    else:
        sales_percentage = 0

    # Users percentage change
    last_month_users = User.objects.filter(date_joined__lt=thirty_days_ago).count()
    if last_month_users > 0:
        users_percentage = ((total_users - last_month_users) / last_month_users) * 100
    else:
        users_percentage = 0

    # Active users percentage change
    last_month_active = User.objects.filter(is_active=True, date_joined__lt=thirty_days_ago).count()
    if last_month_active > 0:
        active_users_percentage = ((active_users - last_month_active) / last_month_active) * 100
    else:
        active_users_percentage = 0

    # Sales data for chart (last 7 days)
    chart_data = []
    chart_labels = []
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        day_sales = Sale.objects.filter(
            status='completed',
            date__date=date.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        chart_data.append(float(day_sales))
        chart_labels.append(date.strftime('%a'))

    # Recent activity (last 10 activities)
    recent_sales = Sale.objects.all().order_by('-date')[:5]
    recent_users = User.objects.all().order_by('-date_joined')[:5]

    # ------------------------------------------------------------------
    # Sales documentation data (for the table in adminDashboard.html)
    # ------------------------------------------------------------------
    # Optional filter by sales manager (?user=<id>)
    sales_manager_id = request.GET.get('user', '')

    sales_qs = Sale.objects.select_related('drug', 'sales_manager').filter(status='completed').order_by('-date')
    if sales_manager_id:
        sales_qs = sales_qs.filter(sales_manager_id=sales_manager_id)

    total_idadi = sales_qs.aggregate(total=Sum('quantity'))['total'] or 0
    total_jumla = sales_qs.aggregate(total=Sum('amount'))['total'] or 0

    # Only sales managers for the filter dropdown
    sales_users = User.objects.filter(role='SALES_MANAGER').order_by('username')

    # Inventory overview
    # If a sales manager is selected, show inventory only for drugs that manager has sold.
    inventory = Inventory.objects.select_related('drug').all().order_by('drug__name')
    if sales_manager_id:
        manager_drug_ids = sales_qs.values_list('drug_id', flat=True).distinct()
        inventory = inventory.filter(drug_id__in=manager_drug_ids)

    # System status (check if system is operational)
    system_status = "Online"

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_sales': total_sales_amount,
        'users_percentage': users_percentage,
        'active_users_percentage': active_users_percentage,
        'sales_percentage': sales_percentage,
        'chart_data': json.dumps(chart_data),
        'chart_labels': json.dumps(chart_labels),
        'recent_sales': recent_sales,
        'recent_users': recent_users,
        'system_status': system_status,
        # Sales documentation table
        'sales': sales_qs,
        'users': sales_users,
        'total_idadi': total_idadi,
        'total_jumla': total_jumla,
        # Inventory overview
        'inventory': inventory,
    }

    return render(request, 'SystemAdmin/adminDashboard.html', context)

@login_required
def user_list(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    User = get_user_model()
    search_query = request.GET.get('search', '')
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    return render(request, 'SystemAdmin/user_list.html', {
        'users': users,
        'search_query': search_query
    })

@login_required
def user_create(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    
    return render(request, 'SystemAdmin/user_form.html', {
        'form': form,
        'title': 'Create User',
        'action': 'Create'
    })

@login_required
def user_edit(request, user_id):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'SystemAdmin/user_form.html', {
        'form': form,
        'user': user,
        'title': 'Edit User',
        'action': 'Update'
    })

@login_required
def user_reset_password(request, user_id):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = PasswordResetForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for {user.username} has been reset successfully!')
            return redirect('user_list')
    else:
        form = PasswordResetForm(user)
    
    return render(request, 'SystemAdmin/user_reset_password.html', {
        'form': form,
        'user': user
    })

@login_required
def user_delete(request, user_id):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'SystemAdmin/user_confirm_delete.html', {'user': user})

@login_required
def stock_list(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    inventory = Inventory.objects.select_related('drug').all().order_by('drug__name')
    
    if search_query:
        inventory = inventory.filter(drug__name__icontains=search_query)
    
    if status_filter:
        filtered_items = []
        for item in inventory:
            if status_filter == 'out_of_stock' and item.quantity <= 0:
                filtered_items.append(item)
            elif status_filter == 'low_stock' and 0 < item.quantity <= item.reorder_level:
                filtered_items.append(item)
            elif status_filter == 'in_stock' and item.quantity > item.reorder_level:
                filtered_items.append(item)
        inventory = filtered_items
    
    return render(request, 'SystemAdmin/stock_list.html', {
        'inventory': inventory,
        'search_query': search_query,
        'status_filter': status_filter
    })

@login_required
def drug_create(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = DrugInventoryForm(request.POST)
        if form.is_valid():
            drug = Drug.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                price=form.cleaned_data['price']
            )
            Inventory.objects.create(
                drug=drug,
                quantity=form.cleaned_data['quantity'],
                reorder_level=form.cleaned_data['reorder_level']
            )
            messages.success(request, f'Drug {drug.name} created successfully!')
            return redirect('stock_list')
    else:
        form = DrugInventoryForm()
    
    return render(request, 'SystemAdmin/drug_form.html', {
        'form': form,
        'title': 'Add New Drug',
        'action': 'Create'
    })

@login_required
def drug_edit(request, drug_id):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    drug = get_object_or_404(Drug, id=drug_id)
    inventory, created = Inventory.objects.get_or_create(drug=drug)
    
    if request.method == 'POST':
        drug_form = DrugForm(request.POST, instance=drug)
        inventory_form = InventoryForm(request.POST, instance=inventory)
        if drug_form.is_valid() and inventory_form.is_valid():
            drug_form.save()
            inventory_form.save()
            messages.success(request, f'Drug {drug.name} updated successfully!')
            return redirect('stock_list')
    else:
        drug_form = DrugForm(instance=drug)
        inventory_form = InventoryForm(instance=inventory)
    
    return render(request, 'SystemAdmin/drug_edit.html', {
        'drug_form': drug_form,
        'inventory_form': inventory_form,
        'drug': drug
    })

@login_required
def drug_delete(request, drug_id):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    drug = get_object_or_404(Drug, id=drug_id)
    
    if request.method == 'POST':
        drug_name = drug.name
        drug.delete()  # This will cascade delete inventory
        messages.success(request, f'Drug {drug_name} deleted successfully!')
        return redirect('stock_list')
    
    return render(request, 'SystemAdmin/drug_confirm_delete.html', {'drug': drug})

@login_required
def sales_list(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    sales = Sale.objects.select_related('drug', 'sales_manager').all().order_by('-date')
    
    if search_query:
        sales = sales.filter(
            Q(order_id__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(drug__name__icontains=search_query)
        )
    
    if status_filter:
        sales = sales.filter(status=status_filter)
    
    if date_from:
        sales = sales.filter(date__date__gte=date_from)
    
    if date_to:
        sales = sales.filter(date__date__lte=date_to)
    
    # Calculate totals
    total_sales = sales.aggregate(total=Sum('amount'))['total'] or 0
    total_orders = sales.count()
    
    return render(request, 'SystemAdmin/sales_list.html', {
        'sales': sales,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales,
        'total_orders': total_orders
    })

@login_required
def sales_documentation(request):
    if request.user.role != 'SYSTEM_ADMIN':
        raise PermissionDenied("You don't have permission to access this page.")
    
    User = get_user_model()
    
    # Get filter parameters
    user_filter = request.GET.get('user', '')
    
    # Get all sales
    sales = Sale.objects.select_related('drug', 'sales_manager').filter(status='completed').order_by('-date')
    
    # Filter by user if specified
    if user_filter:
        sales = sales.filter(sales_manager_id=user_filter)
    
    # Calculate totals
    total_idadi = sales.aggregate(total=Sum('quantity'))['total'] or 0
    total_jumla = sales.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get all users for filter dropdown
    users = User.objects.filter(role='SALES_MANAGER').order_by('username')
    
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_sales_amount = Sale.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    return render(request, 'SystemAdmin/adminDashboard.html', {
        'sales': sales,
        'users': users,
        'total_idadi': total_idadi,
        'total_jumla': total_jumla,
        'total_users': total_users,
        'active_users': active_users,
        'total_sales': total_sales_amount,
    })
