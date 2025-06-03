from django.contrib import admin
from .models import Main

class MainAdmin(admin.ModelAdmin):
    list_display = ('top_word', 'time_processed', 'time', 'text_size')

    list_filter = ('time',)

    # поиск по top_word
    search_fields = ('top_word',)


admin.site.register(Main, MainAdmin)