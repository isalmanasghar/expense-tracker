from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm
import json

def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')

    # Read filter values from the URL
    category = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Apply filters if provided
    if category:
        expenses = expenses.filter(category=category)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total = sum(e.amount for e in expenses)

    # Group by category for the chart
    category_data = (
        expenses
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )

    chart_labels = json.dumps([item['category'] for item in category_data])
    chart_values = json.dumps([float(item['total']) for item in category_data])

    form = ExpenseForm()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
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
    })

def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    return redirect('expense_list')


def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
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