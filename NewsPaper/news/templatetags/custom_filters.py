from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# Список
BAD_WORDS = [
    'редиска', 'дурак', 'негодяй', 'мерзавец', 'подлец',
    'идиот', 'кретин', 'болван', 'невежда', 'хам'
]


@register.filter(name='censor')
@stringfilter  # Фильтр будет применяться только к строкам
def censor(value):
    """
    Фильтр цензурирует нежелательные слова в тексте.
    Заменяет все буквы нежелательного слова на '*', кроме первой.
    Например: "редиска" -> "р******"
    """
    if not isinstance(value, str):
        raise TypeError(f"Фильтр censor может применяться только к строкам. Получен тип: {type(value).__name__}")

    # Разбиваем текст на слова
    words = value.split()
    censored_words = []

    for word in words:
        # Проверяем, есть ли слово в списке нежелательных (без учета регистра)
        word_lower = word.lower().strip('.,!?;:"()')

        if word_lower in BAD_WORDS:

            first_letter = word[0]
            censored_word = first_letter + '*' * (len(word) - 1)

            if word[-1] in '.,!?;:"()':
                censored_word += word[-1]

            censored_words.append(censored_word)
        else:
            censored_words.append(word)

    return ' '.join(censored_words)