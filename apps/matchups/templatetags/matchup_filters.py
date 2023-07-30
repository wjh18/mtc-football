from typing import Mapping

from django import template

register = template.Library()


@register.filter()
def round_name(week_num: int, round_dict: Mapping) -> str:
    # Check if the integer_value exists in the mapping
    return round_dict.get(week_num, "")
