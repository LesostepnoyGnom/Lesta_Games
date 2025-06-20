import os
from django.core.exceptions import ValidationError
from django import forms
from .models import Collection

def validate_file_extension(value):
    valid_extensions = ['.txt']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Недопустимый формат файла. Разрешён только .txt')

def validate_file_size(value):
    limit = 5 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Файл слишком большой. Максимальный размер: 5 MB.')

class UploadFileForm(forms.Form):
    file = forms.FileField(label="файл", validators=[validate_file_extension, validate_file_size])

    #user_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        required=False,
        empty_label="Выберите существующую группу"
    )
    new_collection_name = forms.CharField(
        max_length=255,
        required=False,
        label="Или введите новую группу"
    )

    def __init__(self, *args, **kwargs):
        # Получаем числовой user_id из аргументов
        user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

        # Фильтруем ТОЛЬКО по user_id, если он передан
        if user_id is not None:
            self.fields['collection'].queryset = Collection.objects.filter(user_id=user_id)