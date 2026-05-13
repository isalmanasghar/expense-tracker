from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Expense
from .forms import ExpenseForm
import json

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    category = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if category:
        expenses = expenses.filter(category=category)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total = sum(e.amount for e in expenses)

    category_data = (
        expenses
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )

    monthly_data = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    chart_labels = json.dumps([item['category'] for item in category_data])
    chart_values = json.dumps([float(item['total']) for item in category_data])

    form = ExpenseForm()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'form': form,
        'total': total,
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'monthly_data': monthly_data,
    })

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect('expense_list')

@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    form = ExpenseForm(instance=expense)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')

    return render(request, 'expenses/edit_expense.html', {
        'form': form,
        'expense': expense,
    })

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('expense_list')
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('expense_list')
    return render(request, 'expenses/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('expense_list')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expense_list')
    return render(request, 'expenses/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')