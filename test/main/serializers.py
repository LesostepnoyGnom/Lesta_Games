from rest_framework import serializers

from main.models import Main, Documents, Collection


class MainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Main
        fields = ('top_word', 'time')

class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ['id', 'doc_name']

class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'collection_name']