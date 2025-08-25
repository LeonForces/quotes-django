import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from quotes.models import Quote


@pytest.mark.django_db
def test_source_limit_clean():
    # Допускаются максимум 3 цитаты на один источник (iexact)
    for i in range(3):
        Quote.objects.create(text=f"q{i}", source="SameSource", weight=1)

    q4 = Quote(text="q3", source="SameSource", weight=1)
    with pytest.raises(ValidationError):
        q4.full_clean()  # вызовет model.clean() и упадёт


@pytest.mark.django_db
def test_unique_text_source_case_insensitive():
    # Уникальность по (Lower(text), Lower(source))
    Quote.objects.create(text="Hello", source="Book", weight=1)

    # Дубликат по регистронезависимому правилу должен упасть на уровне БД
    with pytest.raises(IntegrityError):
        Quote.objects.create(text="hello", source="book", weight=1)
