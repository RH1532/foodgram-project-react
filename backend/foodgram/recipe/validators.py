import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from foodgram.settings import FORBIDDEN_USERNAMES


def validate_username(username):
    if username in FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'{username} недопустимое имя пользователя!'
        )
    uncorrect_chars = ''.join(
        set(re.findall(r'[^\w.@+-]', username))
    )
    if uncorrect_chars:
        raise ValidationError(
            f'Некорректные символы в имени {uncorrect_chars}',
        )
    return username