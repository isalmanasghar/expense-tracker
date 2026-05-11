from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
]