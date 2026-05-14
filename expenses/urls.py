from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('export/', views.export_expenses, name='export_expenses'),
]