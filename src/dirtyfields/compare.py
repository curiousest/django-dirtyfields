import datetime
import pytz
import warnings

from django.utils import timezone


def raw_compare(new_value, old_value):
    return new_value == old_value


def timezone_support_compare(new_value, old_value, timezone_to_set=pytz.UTC):

    if not (isinstance(new_value, datetime.datetime) and isinstance(old_value, datetime.datetime)):
        return raw_compare(new_value, old_value)

    db_value_is_aware = timezone.is_aware(old_value)
    in_memory_value_is_aware = timezone.is_aware(new_value)

    if db_value_is_aware == in_memory_value_is_aware:
        return raw_compare(new_value, old_value)

    if db_value_is_aware:
        # If db value is aware, it means that settings.USE_TZ=True, so we need to convert in-memory one
        warnings.warn("DateTimeField received a naive datetime (%s)"
                      " while time zone support is active." % new_value,
                      RuntimeWarning)
        new_value = timezone.make_aware(new_value, timezone_to_set).astimezone(pytz.utc)
    else:
        # The db is not timezone aware, but the value we are passing for comparison is aware.
        warnings.warn("Time zone support is not active (settings.USE_TZ=False), "
                      "and you pass a time zone aware value (%s)"
                      " Converting database value before comparison." % new_value,
                      RuntimeWarning)
        old_value = timezone.make_aware(old_value, pytz.utc).astimezone(timezone_to_set)

    return raw_compare(new_value, old_value)
