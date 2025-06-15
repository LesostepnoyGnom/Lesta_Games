from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import UploadFileForm

from . import functions as fn
from .models import Main, Documents, Collection

import time

def handle_uploaded_file(f):
    #with open(f"uploads/{f.name}", "wb+") as destination:
    file_path = f"uploads/{f.name}"
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

@login_required(login_url='/users/login/')
def index(request):

    if request.method == "POST":

        form = UploadFileForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            file_path = handle_uploaded_file(form.cleaned_data['file'])

            collection = form.cleaned_data['collection']
            new_collection_name = form.cleaned_data['new_collection_name']

            if new_collection_name:
                # Создаём новую группу или получаем существующую с таким именем
                record = Collection(
                    collection_name=new_collection_name,
                    user_id=request.user.id
                )
                record.save()
                collection = new_collection_name
                #collection, created = Collection.objects.get_or_create(collection_name=new_collection_name)

            with open(file_path, 'r', encoding="utf-8") as file:
                text = file.read()

            collection_id = Collection.objects.get(collection_name=collection).id
            record = Documents(
                doc_name=file_path.split("/")[-1],
                user_id=request.user.id,
                collection_id=collection_id
            )
            record.save()

            start_time = time.time()

            all_words, documents = fn.text_prepare(text, collection)
            tf = fn.get_tf(all_words)
            idf = fn.get_idf(all_words, documents)

            rows = [ (tf[0], tf[1], idf[1]) for tf, idf in zip(tf, idf) ]
            rows = sorted(rows, key=lambda x: x[2], reverse=True)

            end_time = time.time()
            delta_time = round(end_time - start_time, 5) # время обработки
            top_word = rows[0][0]
            text_size = len(rows)

            record = Main(
                user_id=request.user.id,
                user_name=request.user.username,
                top_word=top_word,
                time_processed=delta_time,
                text_size=text_size
            )
            record.save()

            data = {"title": "TF-IDF приложение", "rows": rows[:50]}

            return render(request, 'main/table.html', data)
            #return render(request, 'main/file.html', data)

    else:
        form = UploadFileForm(user_id=request.user.id)

    return render(request, 'main/file.html',
                  {"title": "TF-IDF приложение",
                            "form": form})

def test_pg(request):
    return render(request, 'main/test_page.html')