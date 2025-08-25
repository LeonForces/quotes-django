import pytest
from django.urls import reverse

from quotes.models import Quote


@pytest.mark.django_db
def test_popular_sort_by_likes(client):
    # a = Quote.objects.create(text="A", source="S", weight=1, likes=5, views=10, dislikes=2)
    b = Quote.objects.create(text="B", source="S", weight=1, likes=7, views=5, dislikes=1)
    resp = client.get(reverse('popular') + "?sort=likes")
    assert resp.status_code == 200
    quotes = list(resp.context['quotes'])
    assert quotes[0].id == b.id  # больше лайков — выше


@pytest.mark.django_db
def test_popular_sort_by_views(client):
    a = Quote.objects.create(text="A", source="S", weight=1, likes=5, views=10, dislikes=2)
    # b = Quote.objects.create(text="B", source="S", weight=1, likes=7, views=5, dislikes=1)
    resp = client.get(reverse('popular') + "?sort=views")
    assert resp.status_code == 200
    quotes = list(resp.context['quotes'])
    assert quotes[0].id == a.id  # больше просмотров — выше


@pytest.mark.django_db
def test_popular_sort_by_dislikes(client):
    # a = Quote.objects.create(text="A", source="S", weight=1, dislikes=2, likes=1, views=1)
    b = Quote.objects.create(text="B", source="S", weight=1, dislikes=5, likes=1, views=1)
    resp = client.get(reverse('popular') + "?sort=dislikes")
    assert resp.status_code == 200
    quotes = list(resp.context['quotes'])
    assert quotes[0].id == b.id  # больше дизлайков — выше
