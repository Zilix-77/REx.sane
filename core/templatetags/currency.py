"""
Custom template filter for formatting numbers as Indian Rupees.

Usage in templates:
    {% load currency %}
    {{ amount|inr }}        →  ₹1,50,000.00
    {{ amount|inr_short }}  →  ₹1.5L
"""

from django import template
import locale

register = template.Library()


@register.filter
def inr(value):
    """Format a number as ₹XX,XXX.XX using Indian numbering."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    # Indian numbering: last 3 digits, then groups of 2
    is_negative = value < 0
    value = abs(value)
    integer_part = int(value)
    decimal_part = f"{value - integer_part:.2f}"[1:]  # ".XX"

    # Format integer part with Indian commas
    s = str(integer_part)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        # Group remaining digits in pairs from right
        groups = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ','.join(groups) + ',' + last3
    else:
        formatted = s

    sign = '-' if is_negative else ''
    return f"{sign}₹{formatted}{decimal_part}"


@register.filter
def inr_short(value):
    """Format large numbers in short form: ₹1.5L, ₹2.3Cr."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    abs_val = abs(value)
    sign = '-' if value < 0 else ''

    if abs_val >= 1_00_00_000:  # 1 Crore
        return f"{sign}₹{abs_val / 1_00_00_000:.1f}Cr"
    elif abs_val >= 1_00_000:  # 1 Lakh
        return f"{sign}₹{abs_val / 1_00_000:.1f}L"
    elif abs_val >= 1_000:
        return f"{sign}₹{abs_val / 1_000:.1f}K"
    else:
        return f"{sign}₹{abs_val:.0f}"
