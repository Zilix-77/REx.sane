"""
URL routing for the core app.
All routes are simple and flat — no nesting.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('scratchpad/', views.scratchpad, name='scratchpad'),
    path('settings/', views.edit_profile, name='settings'),
]
