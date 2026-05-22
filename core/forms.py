"""
Forms for REx.sane.
Keeps validation logic clean and reusable.
"""

from django import forms
from .models import Profile, Expense


class OnboardingForm(forms.ModelForm):
    """Form for the initial budget setup."""

    class Meta:
        model = Profile
        fields = ['name', 'monthly_income', 'needs_pct', 'wants_pct', 'savings_pct']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Sharma Family',
                'class': 'form-input',
            }),
            'monthly_income': forms.NumberInput(attrs={
                'placeholder': 'e.g. 50000',
                'class': 'form-input',
                'min': '0',
                'step': '100',
            }),
            'needs_pct': forms.NumberInput(attrs={
                'class': 'form-input pct-input',
                'min': '0',
                'max': '100',
            }),
            'wants_pct': forms.NumberInput(attrs={
                'class': 'form-input pct-input',
                'min': '0',
                'max': '100',
            }),
            'savings_pct': forms.NumberInput(attrs={
                'class': 'form-input pct-input',
                'min': '0',
                'max': '100',
            }),
        }

    def clean(self):
        """Make sure the three percentages add up to 100."""
        cleaned = super().clean()
        needs = cleaned.get('needs_pct', 0) or 0
        wants = cleaned.get('wants_pct', 0) or 0
        savings = cleaned.get('savings_pct', 0) or 0
        total = needs + wants + savings
        if total != 100:
            raise forms.ValidationError(
                f"Needs + Wants + Savings must equal 100%. Currently: {total}%."
            )
        return cleaned


class ExpenseForm(forms.ModelForm):
    """Form for adding a new expense."""

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'note']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Groceries, Electric bill...',
                'class': 'form-input',
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1500',
                'class': 'form-input',
                'min': '0.01',
                'step': '0.01',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
            }),
            'note': forms.Textarea(attrs={
                'placeholder': 'Any extra details (optional)',
                'class': 'form-input',
                'rows': 2,
            }),
        }
