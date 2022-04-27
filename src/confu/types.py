"""
Custom data types to help with env variables

Import from this file (confu.types)
"""
import re


class TimeDuration(float):
    """
    takes in and converts a string to float of seconds.
        .5 = 500ms
        90 = 1m30s
    units accepted are d(days), h(hours), m(minutes),
    s(seconds) and ms(milliseconds).
    Can also take a `float`, `int` or `string` without
    unit instead.

    **Arguments**

    - val (`str`, `int` or `float`)
    """

    @classmethod
    def parse_string(self, value):
        re_validate = re.compile(r"(([\d\.]+)((ms)|[smhd]{1}))*")
        value = value.replace(" ", "")
        if not re.fullmatch(re_validate, value):
            raise ValueError(f"unknown unit or format in interval string '{value}'")

        re_intv = re.compile(r"([\d\.]+)((ms)|[smhd]{1})")
        total = 0.0
        for match in re_intv.findall(value):
            unit = match[1]
            count = float(match[0])
            if unit == "s":
                total += count
            elif unit == "m":
                total += count * 60
            elif unit == "ms":
                total += count / 1000
            elif unit == "h":
                total += count * 3600
            elif unit == "d":
                total += count * 86400
        return total

    def __new__(cls, value, **kwargs):
        try:
            return super(TimeDuration, cls).__new__(cls, float(value))
        except ValueError:
            pass
        if not isinstance(value, str):
            raise TypeError("float, int or string expected")

        return super(TimeDuration, cls).__new__(cls, cls.parse_string(value))
