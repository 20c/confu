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
    units accepted are y(years), d(days), h(hours), m(minutes),
    s(seconds) and ms(milliseconds).
    Can also take a `float`, `int` or `string` without
    unit instead.

    **Arguments**

    - val (`str`, `int` or `float`)
    """

    @classmethod
    def parse_string(self, value: str) -> float:
        re_validate = re.compile(r"(([\d\.]+)((ms)|[smhdy]{1}))*")
        value = value.replace(" ", "")
        if not re.fullmatch(re_validate, value):
            raise ValueError(f"unknown unit or format in interval string '{value}'")

        re_intv = re.compile(r"([\d\.]+)((ms)|[smhdy]{1})")
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
            elif unit == "y":
                total += count * 31557600
        return total

    def __new__(cls, value, **kwargs):
        try:
            return super().__new__(cls, float(value))
        except ValueError:
            pass
        if not isinstance(value, str):
            raise TypeError("float, int or string expected")

        return super().__new__(cls, cls.parse_string(value))
