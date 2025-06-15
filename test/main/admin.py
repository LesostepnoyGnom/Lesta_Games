from django.contrib import admin
from .models import Main, Documents, Collection

class MainAdmin(admin.ModelAdmin):
    list_display = ('user_id','user_name', 'top_word', 'time_processed', 'time', 'text_size')

    list_filter = ('time',)

    # поиск по top_word
    search_fields = ('top_word',)


admin.site.register(Main, MainAdmin)

class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc_name', 'user_id', 'collection_id')
    search_fields = ('doc_name',)

admin.site.register(Documents, DocumentsAdmin)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'collection_name', 'user_id')
    search_fields = ('collection_name',)

admin.site.register(Collection, CollectionAdmin)