from django import forms
from .models import Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Текст цитаты'}),
            'source': forms.TextInput(attrs={'placeholder': 'Источник (книга, фильм...)'}),
            'weight': forms.NumberInput(attrs={'min': 1}),
        }

    def clean(self):
        cleaned = super().clean()
        # Доверяем уникальным ограничениям и model.clean()
        # Вызовем их явно, чтобы получить корректные ошибки в форме
        if self.instance is None:
            instance = Quote(**cleaned)
        else:
            for k, v in cleaned.items():
                setattr(self.instance, k, v)
            instance = self.instance

        try:
            instance.full_clean(exclude=None)
        except forms.ValidationError as e:
            raise e
        return cleaned
