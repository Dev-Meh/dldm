from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import Sale, Drug, Inventory
from django.http import JsonResponse
import json


# =========================
# SALES DASHBOARD
# =========================
@login_required
def sales_dashboard(request):
    today = timezone.now().date()

    user_sales = Sale.objects.filter(sales_manager=request.user)

    today_sales = user_sales.filter(date__date=today).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_drugs = Drug.objects.count()
    pending_orders = user_sales.filter(status='pending').count()

    monthly_revenue = user_sales.filter(
        date__month=today.month,
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    recent_sales = user_sales.select_related('drug').order_by('-date')[:10]

    all_drugs = Drug.objects.all().order_by('name')

    available_drugs = Drug.objects.filter(
        inventories__sales_manager=request.user,
        inventories__quantity__gt=0
    ).distinct()

    inventory = Inventory.objects.select_related('drug').filter(
        sales_manager=request.user
    )

    context = {
        'today_sales': today_sales,
        'total_drugs': total_drugs,
        'pending_orders': pending_orders,
        'monthly_revenue': monthly_revenue,
        'recent_sales': recent_sales,
        'available_drugs': available_drugs,
        'all_drugs': all_drugs,
        'inventory': inventory,
        'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return render(request, 'SalesDashboard.html', context)


# =========================
# PROCESS SALE
# =========================
@login_required
def process_sale(request):
    if request.method == 'POST':
        try:
            customer_name = request.POST.get('customer_name')
            items_json = request.POST.get('items', '[]')

            try:
                items = json.loads(items_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid items format'
                })

            if not items:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please add at least one drug'
                })

            validated_items = []

            for item in items:
                drug_id = item.get('drug_id')
                quantity = int(item.get('quantity', 0))

                if not drug_id or quantity <= 0:
                    continue

                drug = Drug.objects.get(id=drug_id)

                inventory, created = Inventory.objects.get_or_create(
                    drug=drug,
                    sales_manager=request.user,
                    defaults={'quantity': 0, 'reorder_level': 10}
                )

                if inventory.quantity < quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient stock for {drug.name}. Available: {inventory.quantity}, Requested: {quantity}'
                    })

                validated_items.append({
                    'drug': drug,
                    'inventory': inventory,
                    'quantity': quantity,
                    'amount': drug.price * quantity
                })

            if not validated_items:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No valid items to process'
                })

            with transaction.atomic():

                last_order = Sale.objects.select_for_update().order_by('-id').first()
                last_num = 0

                if last_order and last_order.order_id:
                    try:
                        last_num = int(last_order.order_id.replace('ORD', ''))
                    except:
                        last_num = 0

                order_id = f"ORD{str(last_num + 1).zfill(6)}"

                total_amount = 0

                for item_data in validated_items:
                    drug = item_data['drug']
                    inventory = item_data['inventory']
                    quantity = item_data['quantity']
                    amount = item_data['amount']

                    total_amount += amount

                    Sale.objects.create(
                        order_id=order_id,
                        customer_name=customer_name,
                        drug=drug,
                        quantity=quantity,
                        amount=amount,
                        status='completed',
                        sales_manager=request.user
                    )

                    inventory.quantity -= quantity
                    inventory.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Sale processed successfully. Order ID: {order_id}',
                'order_id': order_id,
                'total_amount': float(total_amount)
            })

        except Drug.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Drug not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


# =========================
# RECEIPT
# =========================
@login_required
def receipt(request, order_id):
    sales = Sale.objects.filter(order_id=order_id).select_related(
        'drug', 'sales_manager'
    )

    if not sales.exists():
        return redirect('sales_dashboard')

    total_amount = sum(sale.amount for sale in sales)
    total_quantity = sum(sale.quantity for sale in sales)

    first_sale = sales.first()

    context = {
        'order_id': order_id,
        'customer_name': first_sale.customer_name,
        'sale_date': first_sale.date,
        'sales_manager': first_sale.sales_manager,
        'sales': sales,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
    }

    return render(request, 'Salesmanager/receipt.html', context)


# =========================
# GENERATE REPORT
# =========================
@login_required
def generate_report(request):
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(
                request.POST.get('start_date'),
                '%Y-%m-%d'
            ).date()

            end_date = datetime.strptime(
                request.POST.get('end_date'),
                '%Y-%m-%d'
            ).date()

            sales = Sale.objects.filter(
                sales_manager=request.user,
                date__date__range=[start_date, end_date]
            ).select_related('drug')

            total_sales = sales.aggregate(
                total=Sum('amount')
            )['total'] or 0

            sales_by_drug = sales.values(
                'drug__name'
            ).annotate(
                total=Sum('amount'),
                quantity=Sum('quantity')
            )

            return JsonResponse({
                'status': 'success',
                'data': {
                    'total_sales': total_sales,
                    'sales_by_drug': list(sales_by_drug)
                }
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


# =========================
# ADD STOCK
# =========================
@login_required
def add_stock(request):
    if request.method == 'POST':
        try:
            drug_id = request.POST.get('drug_id')
            quantity_to_add = int(request.POST.get('quantity', 0))

            if quantity_to_add <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Quantity must be greater than 0'
                })

            drug = Drug.objects.get(id=drug_id)

            inventory, created = Inventory.objects.get_or_create(
                drug=drug,
                sales_manager=request.user,
                defaults={'quantity': 0, 'reorder_level': 10}
            )

            inventory.quantity += quantity_to_add
            inventory.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Added {quantity_to_add} units of {drug.name}. New stock: {inventory.quantity}'
            })

        except Drug.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Drug not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })