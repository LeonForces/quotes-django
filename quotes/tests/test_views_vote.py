import pytest
from django.urls import reverse

from quotes.models import Quote


@pytest.mark.django_db
def test_like_once(client):
    q = Quote.objects.create(text="T", source="S", weight=1)
    resp = client.post(reverse('vote', args=[q.id, 'like']), data={'next': reverse('random_quote')})
    assert resp.status_code == 302
    q.refresh_from_db()
    assert q.likes == 1
    assert q.dislikes == 0

    # Повторный like не меняет счётчики
    resp = client.post(reverse('vote', args=[q.id, 'like']), data={'next': reverse('random_quote')})
    assert resp.status_code == 302
    q.refresh_from_db()
    assert q.likes == 1
    assert q.dislikes == 0


@pytest.mark.django_db
def test_toggle_like_to_dislike(client):
    q = Quote.objects.create(text="T", source="S", weight=1)

    client.post(reverse('vote', args=[q.id, 'like']), data={'next': reverse('random_quote')})
    q.refresh_from_db()
    assert q.likes == 1 and q.dislikes == 0

    client.post(reverse('vote', args=[q.id, 'dislike']), data={'next': reverse('random_quote')})
    q.refresh_from_db()
    assert q.likes == 0 and q.dislikes == 1  # переключение учтено корректно


@pytest.mark.django_db
def test_toggle_dislike_to_like(client):
    q = Quote.objects.create(text="T", source="S", weight=1)

    client.post(reverse('vote', args=[q.id, 'dislike']), data={'next': reverse('random_quote')})
    q.refresh_from_db()
    assert q.likes == 0 and q.dislikes == 1

    client.post(reverse('vote', args=[q.id, 'like']), data={'next': reverse('random_quote')})
    q.refresh_from_db()
    assert q.likes == 1 and q.dislikes == 0
