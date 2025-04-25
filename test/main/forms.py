import os
from django.core.exceptions import ValidationError
from django import forms
from django.core.validators import FileExtensionValidator

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