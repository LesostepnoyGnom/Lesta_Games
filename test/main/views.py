from django.db.models import Count, Min, Avg, Max
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView

from .forms import UploadFileForm
from rest_framework.response import Response

from . import functions as fn
from .models import Main
from .serializers import MainSerializer

import time

def handle_uploaded_file(f):
    #with open(f"uploads/{f.name}", "wb+") as destination:
    with open("uploads/text", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def index(request):

    if request.method == "POST":

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])

            start_time = time.time()

            all_words, documents = fn.text_prepare("uploads/text")
            tf = fn.get_tf(all_words)
            idf = fn.get_idf(all_words, documents)

            rows = [ (tf[0], tf[1], idf[1]) for tf, idf in zip(tf, idf) ]
            rows = sorted(rows, key=lambda x: x[2], reverse=True)

            end_time = time.time()
            delta_time = round(end_time - start_time, 5) # время обработки
            top_word = rows[0][0]
            text_size = len(rows)

            record = Main(
                top_word=top_word,
                time_processed=delta_time,
                text_size=text_size
            )
            record.save()

            data = {"title": "Lesta Game тестовое задание", "rows": rows[:50]}

            return render(request, 'main/table.html', data)

    else:
        form = UploadFileForm()

    return render(request, 'main/file.html',
                  {"title": "Lesta Game тестовое задание",
                            "form": form})

def test_pg(request):
    return render(request, 'main/test_page.html')

class MainAPIView(APIView):
    def get(self, request):
        return Response({'status': 'OK'})

class MainAPIViewVersion(APIView):
    def get(self, request):
        return Response({'version': '2.0.0'})

class MainAPIViewMetrics(APIView):
    def get(self, request):
        files_processed = Main.objects.aggregate(total=Count('*'))['total']
        min_time_processed = Main.objects.aggregate(min_time=Min('time_processed'))['min_time']
        avg_time_processed = round(Main.objects.aggregate(avg_time=Avg('time_processed'))['avg_time'], 5)
        max_time_processed = Main.objects.aggregate(max_time=Max('time_processed'))['max_time']
        latest_file_processed_timestamp = Main.objects.aggregate(latest_time=Max('time'))['latest_time'].timestamp()

        max_len_text = Main.objects.aggregate(max_len=Max('text_size'))['max_len']
        avg_len_text = round(Main.objects.aggregate(avg_len=Avg('text_size'))['avg_len'], 5)

        return Response({'files_processed': files_processed,
                         'min_time_processed': min_time_processed,
                         'avg_time_processed': avg_time_processed,
                         'max_time_processed': max_time_processed,
                         'latest_file_processed_timestamp': latest_file_processed_timestamp,
                         'max_len_text': max_len_text,
                         'avg_len_text': avg_len_text
                         })


#class MainAPIView(generics.ListAPIView):
#    queryset = Main.objects.all()
#    serializer_class = MainSerializer
