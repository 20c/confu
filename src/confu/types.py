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

    **Arguments**

    - val (`str`)
    """
    def __new__(cls, value, **kwargs):
        re_intv = re.compile(r"([\d\.]+)([a-zA-Z]+)")
        re_validate = re.compile(r"(([\d\.]+)([s,m,ms,h,d]+))*")
        formatted_val = value.replace(" ", "")

        total = 0.0
        if not re.fullmatch(re_validate, formatted_val):
            raise ValueError("unknown unit or format in interval string '%s'" % value)
        for match in re_intv.findall(formatted_val):
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
        return super(TimeDuration, cls).__new__(cls, total)
