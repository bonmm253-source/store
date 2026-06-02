from django import template

register = template.Library()

@register.filter
def to_thousands(value):
    """Convert a number to thousands format (e.g., 50000 -> 50K)"""
    try:
        value = float(value)
        if value >= 1000:
            return f"{value/1000:.0f}K"
        return f"{value:.0f}"
    except (ValueError, TypeError):
        return value
