"""
Models for REx.sane budgeting app.

Three models:
- Profile: household budget settings (singleton — one row)
- Expense: individual spending entries
- ScratchPad: free-form notes (singleton — one row)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    """
    Stores the household's budget configuration.
    Only one Profile row should exist (singleton pattern).
    """
    name = models.CharField(
        max_length=100,
        help_text="Your name or family name"
    )
    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Your total monthly income after taxes"
    )
    needs_pct = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of income for needs (rent, groceries, bills)"
    )
    wants_pct = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of income for wants (eating out, shopping)"
    )
    savings_pct = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of income for savings & debt repayment"
    )
    onboarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Budget Profile"

    def __str__(self):
        return f"{self.name}'s Budget"

    @property
    def needs_budget(self):
        """How much money is allocated to needs."""
        return round(float(self.monthly_income) * self.needs_pct / 100, 2)

    @property
    def wants_budget(self):
        """How much money is allocated to wants."""
        return round(float(self.monthly_income) * self.wants_pct / 100, 2)

    @property
    def savings_budget(self):
        """How much money is allocated to savings."""
        return round(float(self.monthly_income) * self.savings_pct / 100, 2)

    @classmethod
    def get_instance(cls):
        """Get the singleton Profile, or None if not yet created."""
        return cls.objects.first()


class Expense(models.Model):
    """A single spending entry."""

    CATEGORY_CHOICES = [
        ('NEED', 'Need'),
        ('WANT', 'Want'),
        ('SAVING', 'Saving'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="What did you spend on?"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="How much did you spend?"
    )
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        help_text="Is this a need, want, or saving?"
    )
    date = models.DateField(
        help_text="When did you spend this?"
    )
    note = models.TextField(
        blank=True,
        default='',
        help_text="Any extra details (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} — ₹{self.amount}"


class ScratchPad(models.Model):
    """
    Free-form notepad for jotting down thoughts.
    Singleton — only one row should exist.
    """
    content = models.TextField(
        blank=True,
        default='',
        help_text="Your notes, shopping lists, reminders..."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Scratch Pad"

    def __str__(self):
        return f"ScratchPad (updated {self.updated_at})"

    @classmethod
    def get_instance(cls):
        """Get or create the singleton ScratchPad."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
