import random
from urllib.parse import urlencode
from django.contrib import messages
from django.db.models import F, Sum, Case, When, Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import QuoteForm
from .models import Quote


def random_quote(request):
    quote_id = request.GET.get('id')
    no_view = request.GET.get('no_view') in ('1', 'true', 'yes')

    quote = None
    if quote_id:
        # Показать конкретную цитату (например, после голосования)
        quote = get_object_or_404(Quote, pk=quote_id)
        # Просмотры не увеличиваем, если указано no_view=1
        if not no_view:
            Quote.objects.filter(pk=quote.pk).update(views=F('views') + 1)
            quote.refresh_from_db(fields=['views'])
        return render(request, 'quotes/random.html', {'quote': quote})

    # Новый параметр: исключить конкретную цитату из случайного выбора
    exclude_id = request.GET.get('exclude')
    qs = Quote.objects.all()
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)

    # Выбрать случайную цитату по весам из qs (с учётом исключения)
    total = qs.aggregate(total=Sum('weight'))['total'] or 0
    if total > 0:
        threshold = random.randint(1, total)
        cumulative = 0
        for q in qs.order_by('id').only('id', 'weight').iterator():
            cumulative += q.weight
            if cumulative >= threshold:
                quote = Quote.objects.get(pk=q.id)
                break

    if quote is None:
        return render(request, 'quotes/random.html', {'quote': None})

    # Инкремент просмотров только при «обычном» заходе
    Quote.objects.filter(pk=quote.pk).update(views=F('views') + 1)
    quote.refresh_from_db(fields=['views'])

    return render(request, 'quotes/random.html', {'quote': quote})


def submit_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Цитата успешно добавлена!')
            return redirect('random_quote')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = QuoteForm()
    return render(request, 'quotes/submit.html', {'form': form})


# Модуль: quotes/views.py — обновляем импорты и функцию vote


def vote(request, quote_id, action):
    if request.method != 'POST':
        return HttpResponseBadRequest('Метод не поддерживается')

    if action not in ('like', 'dislike'):
        return HttpResponseBadRequest('Некорректное действие')

    quote = get_object_or_404(Quote, pk=quote_id)

    # Новое хранение: карта голосов по цитатам в рамках сессии
    session_key = 'votes_map'
    votes_map = request.session.get(session_key, {})
    prev = votes_map.get(str(quote_id))  # 'like' | 'dislike' | None

    if prev == action:
        # Ничего не меняем, уже такой же голос
        if action == 'like':
            messages.info(request, 'Вы уже поставили лайк этой цитате.')
        else:
            messages.info(request, 'Вы уже поставили дизлайк этой цитате.')
    elif prev is None:
        # Первый голос по этой цитате
        if action == 'like':
            Quote.objects.filter(pk=quote.pk).update(likes=F('likes') + 1)
            messages.success(request, 'Лайк засчитан!')
        else:
            Quote.objects.filter(pk=quote.pk).update(dislikes=F('dislikes') + 1)
            messages.success(request, 'Дизлайк засчитан!')
        votes_map[str(quote_id)] = action
        request.session[session_key] = votes_map
        request.session.modified = True
    else:
        # Переключение голоса: like -> dislike или dislike -> like
        if prev == 'like' and action == 'dislike':
            Quote.objects.filter(pk=quote.pk).update(
                likes=Case(When(likes__gt=0, then=F('likes') - 1), default=0),
                dislikes=F('dislikes') + 1,
            )
            messages.success(request, 'Изменили голос на дизлайк.')
        elif prev == 'dislike' and action == 'like':
            Quote.objects.filter(pk=quote.pk).update(
                dislikes=Case(When(dislikes__gt=0, then=F('dislikes') - 1), default=0),
                likes=F('likes') + 1,
            )
            messages.success(request, 'Изменили голос на лайк.')
        votes_map[str(quote_id)] = action
        request.session[session_key] = votes_map
        request.session.modified = True

    next_url = request.POST.get('next') or reverse('random_quote')
    return redirect(next_url)


# Новая вьюха: топ-10 по лайкам (для маршрута 'popular/')
def popular(request):
    sort = request.GET.get('sort', 'likes')
    valid_sorts = {
        'likes': ('-likes', '-views', '-created_at'),
        'views': ('-views', '-likes', '-created_at'),
        'dislikes': ('-dislikes', '-views', '-created_at'),
    }
    order = valid_sorts.get(sort, valid_sorts['likes'])

    qs = Quote.objects.all().order_by(*order)
    source = request.GET.get('source')
    if source:
        qs = qs.filter(source__iexact=source)

    top_quotes = qs[:10]
    sources = Quote.objects.values_list('source', flat=True).distinct().order_by('source')
    return render(
        request,
        'quotes/popular.html',
        {
            'quotes': top_quotes,
            'sources': sources,
            'selected_source': source,
            'sort': sort,
        },
    )


# Новые вьюхи: топ-10 по просмотрам и по дизлайкам, и дашборд
def popular_by_views(request):
    source = request.GET.get('source')
    params = {'sort': 'views'}
    if source:
        params['source'] = source
    return redirect(f"{reverse('popular')}?{urlencode(params)}")

    qs = Quote.objects.all().order_by('-views', '-likes', '-created_at')
    source = request.GET.get('source')
    if source:
        qs = qs.filter(source__iexact=source)

    top_quotes = qs[:10]
    sources = Quote.objects.values_list('source', flat=True).distinct().order_by('source')
    return render(
        request,
        'quotes/popular_views.html',
        {'quotes': top_quotes, 'sources': sources, 'selected_source': source}
    )


def popular_by_dislikes(request):
    source = request.GET.get('source')
    params = {'sort': 'dislikes'}
    if source:
        params['source'] = source
    return redirect(f"{reverse('popular')}?{urlencode(params)}")

    qs = Quote.objects.all().order_by('-dislikes', '-views', '-created_at')
    source = request.GET.get('source')
    if source:
        qs = qs.filter(source__iexact=source)

    top_quotes = qs[:10]
    sources = Quote.objects.values_list('source', flat=True).distinct().order_by('source')
    return render(
        request,
        'quotes/popular_dislikes.html',
        {'quotes': top_quotes, 'sources': sources, 'selected_source': source}
    )


def dashboard(request):
    # Сводные метрики
    agg = Quote.objects.aggregate(
        quotes_count=Count('id'),
        total_views=Sum('views'),
        total_likes=Sum('likes'),
        total_dislikes=Sum('dislikes'),
    )
    # Мини-топы (по 5)
    top_likes = Quote.objects.all().order_by('-likes', '-views', '-created_at')[:5]
    top_views = Quote.objects.all().order_by('-views', '-likes', '-created_at')[:5]
    top_dislikes = Quote.objects.all().order_by('-dislikes', '-views', '-created_at')[:5]

    return render(
        request,
        'quotes/dashboard.html',
        {
            'metrics': agg,
            'top_likes': top_likes,
            'top_views': top_views,
            'top_dislikes': top_dislikes,
        },
    )
