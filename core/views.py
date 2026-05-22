"""
Views for REx.sane budgeting app.

Each view is a simple function — easy to read and modify.
No class-based views to keep things beginner-friendly.
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Profile, Expense, ScratchPad
from .forms import OnboardingForm, ExpenseForm


# ---------------------------------------------------------------------------
# Helper: check if user has completed onboarding
# ---------------------------------------------------------------------------
def _require_onboarding(request):
    """Returns a redirect to onboarding if Profile doesn't exist, else None."""
    profile = Profile.get_instance()
    if not profile or not profile.onboarded:
        return redirect('core:onboarding')
    return None


def _get_month_range(year, month):
    """Return (first_day, last_day) for a given year/month."""
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    return first_day, last_day


# ---------------------------------------------------------------------------
# Home — redirects to dashboard or onboarding
# ---------------------------------------------------------------------------
def home(request):
    """Landing page — redirect based on onboarding status."""
    profile = Profile.get_instance()
    if not profile or not profile.onboarded:
        return redirect('core:onboarding')
    return redirect('core:dashboard')


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------
def onboarding(request):
    """Step-by-step budget setup."""
    profile = Profile.get_instance()

    # If already onboarded, allow re-editing via settings page
    if profile and profile.onboarded:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = OnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.onboarded = True
            profile.save()
            return redirect('core:dashboard')
    else:
        form = OnboardingForm(instance=profile)

    return render(request, 'onboarding.html', {'form': form})


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def dashboard(request):
    """Visual overview of the current month's budget."""
    redir = _require_onboarding(request)
    if redir:
        return redir

    profile = Profile.get_instance()
    today = date.today()

    # Allow month navigation via query params
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    first_day, last_day = _get_month_range(year, month)

    # Aggregate expenses by category for this month
    expenses = Expense.objects.filter(date__gte=first_day, date__lte=last_day)

    spent_by_category = {}
    for cat_code, cat_label in Expense.CATEGORY_CHOICES:
        total = expenses.filter(category=cat_code).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        spent_by_category[cat_code] = float(total)

    needs_spent = spent_by_category.get('NEED', 0)
    wants_spent = spent_by_category.get('WANT', 0)
    savings_spent = spent_by_category.get('SAVING', 0)
    total_spent = needs_spent + wants_spent + savings_spent

    # Budget amounts
    needs_budget = profile.needs_budget
    wants_budget = profile.wants_budget
    savings_budget = profile.savings_budget

    # Daily spending for bar chart (last 30 days within the month)
    daily_spending = []
    daily_labels = []
    current = first_day
    while current <= last_day:
        day_total = expenses.filter(date=current).aggregate(
            total=Sum('amount')
        )['total'] or 0
        daily_labels.append(current.strftime('%d %b'))
        daily_spending.append(float(day_total))
        current += timedelta(days=1)

    # Recent expenses (last 5)
    recent_expenses = expenses[:5]

    # Month navigation
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    context = {
        'profile': profile,
        'current_month': date(year, month, 1),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'is_current_month': (year == today.year and month == today.month),

        # Budget vs Spent
        'needs_budget': needs_budget,
        'needs_spent': needs_spent,
        'needs_remaining': needs_budget - needs_spent,
        'wants_budget': wants_budget,
        'wants_spent': wants_spent,
        'wants_remaining': wants_budget - wants_spent,
        'savings_budget': savings_budget,
        'savings_spent': savings_spent,
        'savings_remaining': savings_budget - savings_spent,
        'total_spent': total_spent,
        'total_budget': float(profile.monthly_income),

        # Chart data (as JSON for JavaScript)
        'doughnut_data': json.dumps([needs_spent, wants_spent, savings_spent]),
        'doughnut_budget': json.dumps([needs_budget, wants_budget, savings_budget]),
        'bar_labels': json.dumps(daily_labels),
        'bar_data': json.dumps(daily_spending),

        # Recent expenses
        'recent_expenses': recent_expenses,

        # Active page for nav highlighting
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard.html', context)


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
def expenses(request):
    """List and add expenses."""
    redir = _require_onboarding(request)
    if redir:
        return redir

    profile = Profile.get_instance()
    today = date.today()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:expenses')
    else:
        form = ExpenseForm(initial={'date': today})

    # Filter by category if requested
    category_filter = request.GET.get('category', '')
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    first_day, last_day = _get_month_range(year, month)

    expense_list = Expense.objects.filter(date__gte=first_day, date__lte=last_day)
    if category_filter:
        expense_list = expense_list.filter(category=category_filter)

    # Month total
    month_total = expense_list.aggregate(total=Sum('amount'))['total'] or 0

    # Month navigation
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    context = {
        'form': form,
        'expenses': expense_list,
        'month_total': month_total,
        'category_filter': category_filter,
        'current_month': date(year, month, 1),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'is_current_month': (year == today.year and month == today.month),
        'profile': profile,
        'active_page': 'expenses',
    }
    return render(request, 'expenses.html', context)


@require_POST
def delete_expense(request, expense_id):
    """Delete a single expense and redirect back to list."""
    expense = get_object_or_404(Expense, pk=expense_id)
    expense.delete()
    return redirect('core:expenses')


# ---------------------------------------------------------------------------
# Scratchpad
# ---------------------------------------------------------------------------
def scratchpad(request):
    """Free-form notepad with auto-save."""
    redir = _require_onboarding(request)
    if redir:
        return redir

    pad = ScratchPad.get_instance()

    if request.method == 'POST':
        # Support AJAX save
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            pad.content = data.get('content', '')
            pad.save()
            return JsonResponse({'status': 'saved', 'updated_at': pad.updated_at.isoformat()})
        else:
            pad.content = request.POST.get('content', '')
            pad.save()
            return redirect('core:scratchpad')

    context = {
        'pad': pad,
        'profile': Profile.get_instance(),
        'active_page': 'scratchpad',
    }
    return render(request, 'scratchpad.html', context)


# ---------------------------------------------------------------------------
# Settings (edit profile)
# ---------------------------------------------------------------------------
def edit_profile(request):
    """Edit budget settings after onboarding."""
    redir = _require_onboarding(request)
    if redir:
        return redir

    profile = Profile.get_instance()

    if request.method == 'POST':
        form = OnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('core:settings')
    else:
        form = OnboardingForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'active_page': 'settings',
    }
    return render(request, 'settings.html', context)
