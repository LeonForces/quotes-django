import pytest
from django.urls import reverse

from quotes.models import Quote


@pytest.mark.django_db
def test_submit_creates_quote(client):
    resp = client.post(reverse('submit_quote'), data={
        'text': 'New quote',
        'source': 'Some Book',
        'weight': 2,
    })
    # Успешная форма редиректит на random
    assert resp.status_code in (302, 303)
    assert Quote.objects.filter(text='New quote', source='Some Book').exists()


@pytest.mark.django_db
def test_submit_source_limit(client):
    for i in range(3):
        Quote.objects.create(text=f"T{i}", source="Limited", weight=1)

    resp = client.post(reverse('submit_quote'), data={
        'text': 'T3',
        'source': 'Limited',
        'weight': 1,
    })
    # Форма должна быть невалидной и остаться на странице
    assert resp.status_code == 200
    # Количество записей не увеличилось
    assert Quote.objects.filter(source__iexact='Limited').count() == 3
