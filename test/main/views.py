from django.shortcuts import render
from .forms import UploadFileForm

from . import functions as fn

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
            all_words, documents = fn.text_prepare("uploads/text")
            tf = fn.get_tf(all_words)
            idf = fn.get_idf(all_words, documents)

            rows = [ (tf[0], tf[1], idf[1]) for tf, idf in zip(tf, idf) ]
            rows = sorted(rows, key=lambda x: x[2], reverse=True)

            data = {"title": "Lesta Game тестовое задание", "rows": rows[:50]}

            return render(request, 'main/table.html', data)

    else:
        form = UploadFileForm()

    return render(request, 'main/file.html',
                  {"title": "Lesta Game тестовое задание",
                            "form": form})

def test_pg(request):
    return render(request, 'main/test_page.html')