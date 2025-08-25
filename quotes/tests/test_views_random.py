import pytest
from django.urls import reverse

from quotes.models import Quote


@pytest.mark.django_db
def test_random_increments_views(client):
    q = Quote.objects.create(text="T1", source="S", weight=1)
    resp = client.get(reverse('random_quote'))
    assert resp.status_code == 200
    q.refresh_from_db()
    assert q.views == 1


@pytest.mark.django_db
def test_no_view_when_open_by_id_with_no_view(client):
    q = Quote.objects.create(text="T2", source="S", weight=1)
    url = reverse('random_quote') + f"?id={q.id}&no_view=1"
    resp = client.get(url)
    assert resp.status_code == 200
    q.refresh_from_db()
    assert q.views == 0  # не увеличивается при no_view=1


@pytest.mark.django_db
def test_exclude_shows_different_quote(client, monkeypatch):
    q1 = Quote.objects.create(text="A", source="S", weight=1)
    q2 = Quote.objects.create(text="B", source="S", weight=1)
    # форсируем выбор первого по порядку (threshold=1)
    monkeypatch.setattr('quotes.views.random.randint', lambda a, b: 1)
    resp = client.get(reverse('random_quote') + f"?exclude={q1.id}")
    assert resp.status_code == 200
    # В контексте должен быть выбран q2, т.к. q1 исключён
    assert resp.context['quote'].id == q2.id
