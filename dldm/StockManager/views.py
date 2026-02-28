from django.shortcuts import render

# Create your views here.

def stock_dashboard(request):
    return render(request, 'StockManager/StockManager.html')
