from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Quote(models.Model):
    text = models.TextField(verbose_name='Текст цитаты')
    source = models.CharField(max_length=255, verbose_name='Источник (книга, фильм и т.п.)')
    weight = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Вес (чем больше, тем чаще показывается)'
    )
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    likes = models.PositiveIntegerField(default=0, verbose_name='Лайки')
    dislikes = models.PositiveIntegerField(default=0, verbose_name='Дизлайки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('text'), Lower('source'),
                name='uq_quote_text_source_ci'
            ),
        ]
        ordering = ['-likes', '-views', '-created_at']

    def clean(self):
        # Проверка лимита в 3 цитаты на источник (case-insensitive)
        same_source_qs = Quote.objects.filter(source__iexact=self.source)
        if self.pk:
            same_source_qs = same_source_qs.exclude(pk=self.pk)
        if same_source_qs.count() >= 3:
            raise ValidationError('У одного источника не может быть более трёх цитат.')

    def __str__(self):
        return f'[{self.source}] {self.text[:50]}'
