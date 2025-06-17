from .serializers import DocumentsSerializer
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Min, Avg, Max

from collections import Counter
from heapq import heapify, heappop, heappush

from .models import Main, Documents, Collection
from . import functions as fn

class MainAPIView(APIView):

    @swagger_auto_schema(
        operation_description="""
                    Возвращает статус приложения
                    """,
        responses={200: "Статус работы приложения"})

    def get(self, request):
        return Response({'status': 'OK'})

class MainAPIViewVersion(APIView):

    @swagger_auto_schema(
        operation_description="""
                Возвращает версию приложения
                """,
        responses={200: "Версия приложения"}
    )

    def get(self, request):
        return Response({'version': '4.4.0'})

class MainAPIViewMetrics(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="""
            ## Метрики обработки файлов  

            Возвращает статистику по обработанным файлам:  
            - Общее количество файлов  
            - Минимальное время обработки  
            - Среднее время обработки  
            - Максимальное время обработки  
            - timestamp обработки файла  
            - Максимальный размер текста
            - Средний размер текста  

            **Пример ответа:**  
            ```json
            {
                "files_processed": 100,
                "min_time_processed": 0.1,
                "avg_time_processed": 0.5,
                "max_time_processed": 2.3,
                "latest_file_processed_timestamp": 1672531200,
                "max_len_text": 1024,
                "avg_len_text": 512.5
            }
            ```
            """,
        responses={200: "Статистика обработки файлов"}
    )

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

class MainAPIViewDocuments(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает список документов, загруженных текущим пользователем",)
    def get(self, request):
        docs = Documents.objects.filter(user_id=request.user.id)
        serializer = DocumentsSerializer(docs, many=True)
        return Response(serializer.data)

class MainAPIViewDocumentsID(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает документ пользователя по id документа",)
    def get(self, request, doc_id):
        doc = Documents.objects.filter(user_id=request.user.id, id=doc_id)

        if not doc.exists():
            return Response({"error": "Документ не найден"}, status=404)

        doc_name = DocumentsSerializer(doc.first()).data["doc_name"]

        with open(f'./uploads/{doc_name}', "r", encoding='UTF-8') as file:
            text = file.read()

        return Response({"doc_name": text})

class MainAPIViewDocumentDelete(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Удаляет документ по его id среди доступных пользователю документов",
        responses={
            200: "Документ успешно удален",
            404: "Документ не найден"
        }
    )
    def delete(self, request, doc_id):
        try:
            document = Documents.objects.get(id=doc_id, user_id=request.user.id)
            document.delete()
            return Response({"error": "Документ успешно удален"})

        except Documents.DoesNotExist:
            return Response({"error": "Документ не найден"})

class MainAPIViewCollection(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает список коллекций пользователя с id коллекций и списком входящих в них документов",)
    def get(self, request):
        collections = Collection.objects.filter(user_id=request.user.id)
        result = []
        for collection in collections:
            documents = Documents.objects.filter(collection_id=collection.id).values_list('id', flat=True)
            result.append({
                "collection_id": collection.id,
                "collection_name": collection.collection_name,
                "documents": documents
            })
        return Response(result)

class MainAPIViewCollectionID(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает список id доступных пользователю документов, входящих в конкретную коллекцию",)
    def get(self, request, coll_id):
        exists = Collection.objects.filter(id=coll_id, user_id=request.user.id).exists()
        if not exists:
            return Response({"error": "Такая коллекция не найдена"}, status=404)

        docs = Documents.objects.filter(collection_id=coll_id)

        if not docs.exists():
            return Response({"error": "Такая коллекция пуста"}, status=404)

        docs = docs.values_list('id', flat=True)

        return Response(docs)

class MainAPIViewChangeCollection(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="""Изменяет коллекцию у выбранного документа из доступных пользователю
                                                  Где coll_id - новая коллекция
                                                  doc_id - id документа у которого меняем коллекицю""", )
    def post(self, request, coll_id, doc_id):
        try:

            if coll_id not in Collection.objects.filter(user_id=request.user.id).values_list('id', flat=True):
                return Response({"error": "Коллекция не найдена"})
            document = Documents.objects.get(id=doc_id, user_id=request.user.id)

            document.collection_id = coll_id
            document.save()

            return Response({"error": "Коллекция документа успешно изменена"})

        except Documents.DoesNotExist:
            return Response({"error": "Документ не найден"})

        except Collection.DoesNotExist:
            return Response({"error": "Коллекция не найдена"})


class MainAPIViewDelCollection(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Удаляет документ из выбранной коллекции из доступных пользователю", )
    def post(self, request, doc_id):
        try:
            document = Documents.objects.get(id=doc_id, user_id=request.user.id)
            document.collection_id = None
            document.save()
            return Response({"error": "Документ успешно удалён из коллекции"})

        except Documents.DoesNotExist:
            return Response({"error": "Документ не найден"})


class MainAPIViewCollectionStat(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает tf-idf по выбранной коллекции",)
    def get(self, request, coll_id):
        exists = Collection.objects.filter(id=coll_id, user_id=request.user.id).exists()
        if not exists:
            return Response({"error": "Такая коллекция не найдена"}, status=404)

        docs = Documents.objects.filter(collection_id=coll_id)

        if not docs.exists():
            return Response({"error": "Такая коллекция пуста"}, status=404)

        docs = docs.values_list('doc_name', flat=True)

        whole_text = ""
        for doc_name in docs:
            with open(f"uploads/{doc_name}", 'r', encoding="utf-8") as file:
                text = file.read()
                whole_text += text

        coll_name = Collection.objects.filter(id=coll_id).values_list('collection_name', flat=True).first()
        all_words, documents = fn.text_prepare(text=whole_text, collection_name=coll_name)

        idf = fn.get_idf(all_words, documents)
        tf = fn.get_tf(all_words)

        rows = [(tf[0], tf[1], idf[1]) for tf, idf in zip(tf, idf)]
        rows = sorted(rows, key=lambda x: x[2], reverse=True)

        json = [ {"word": row[0], "tf": row[1], "idf": row[2]} for row in rows]

        return Response(json)

class MainAPIViewDocumentStat(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает tf-idf по выбранному документу",)
    def get(self, request, doc_id):
        doc = Documents.objects.filter(user_id=request.user.id, id=doc_id)

        if not doc.exists():
            return Response({"error": "Документ не найден"}, status=404)

        doc_name = DocumentsSerializer(doc.first()).data["doc_name"]

        with open(f'./uploads/{doc_name}', "r", encoding='UTF-8') as file:
            text = file.read()

        coll_id = doc.values_list('collection_id', flat=True).first()
        coll_name = Collection.objects.filter(id=coll_id).values_list('collection_name', flat=True).first()

        all_words, documents = fn.text_prepare(text=text, collection_name=coll_name)

        idf = fn.get_idf(all_words, documents)
        tf = fn.get_tf(all_words)

        rows = [(tf[0], tf[1], idf[1]) for tf, idf in zip(tf, idf)]
        rows = sorted(rows, key=lambda x: x[2], reverse=True)

        json = [{"word": row[0], "tf": row[1], "idf": row[2]} for row in rows]

        return Response(json)

class MainAPIViewLogout(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Выходит из аккаунта пользователя", )
    def get(self, request):
        logout(request)
        return Response({'success': 'Успешный выход из системы'})

class MainAPIViewLogin(APIView):
    @swagger_auto_schema(operation_description="Авторизация по логину и паролю", )
    def post(self, request, user_login, user_password):

        user = authenticate(username=user_login, password=user_password)

        if user is not None:
            login(request, user)
            return Response({'success': 'Авторизация успешна'})

        else:
            return Response({'error': 'Неверные учетные данные'})

class MainAPIViewRegister(APIView):
    @swagger_auto_schema(operation_description="Регистрация пользователя", )
    def post(self, request, user_login, user_password):
        try:
            user = User.objects.create_user(username=user_login, password=user_password)
            user.save()

            return Response({'success': 'Аккаунт создан'})
        except Exception as e:
            return Response({'error': f'Ошибка при создании пользователя: {str(e)}'})

class MainAPIViewUser(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Смена пароля текущего пользователя",)
    def patch(self, request, user_password, new_user_password):
        user = request.user

        if not user.check_password(user_password):
            return Response(
                {'error': 'Текущий пароль указан неверно'})

        try:
            user.set_password(new_user_password)
            user.save()

            update_session_auth_hash(request, user)

            return Response(
                {'success': 'Пароль успешно изменен'})

        except Exception as e:
            return Response({'error': f'Ошибка при изменении пароля: {str(e)}'})

class MainAPIViewUserDelete(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Удаляет пользователя",)
    def delete(self, request, user_password):

        user = request.user
        if not user.check_password(user_password):
            return Response(
                {'error': 'Текущий пароль указан неверно'})
        try:
            documents = Documents.objects.filter(user_id=request.user.id)

            coll_id = list(documents.values_list('collection_id', flat=True))
            collections = Collection.objects.filter(id__in=coll_id)
            collections.delete()
            documents.delete()


            request.user.delete()
            logout(request)

            return Response({'success': 'Текущий аккаунт удалён'})

        except Exception as e:
            return Response({'error': f'Ошибка: {str(e)}'})

class MainAPIViewHuffman(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Возвращает содержимое документа, закодированное Кодом Хаффмана",)
    def get(self, request, doc_id):
        doc = Documents.objects.filter(user_id=request.user.id, id=doc_id)

        if not doc.exists():
            return Response({"error": "Документ не найден"}, status=404)

        doc_name = DocumentsSerializer(doc.first()).data["doc_name"]

        with open(f'./uploads/{doc_name}', "r", encoding='UTF-8') as file:
            text = file.read()

        class Node:
            """
            Элемент дерева символов для алгоритма Хаффмана. Содержит символ текста,
            частоту его повторения и массив непосредственных потомков в дереве.
            Объекты можно сравнивать. Сравнение производится по частоте повторения,
            либо по номерам символов в Unicode, если частоты равны.
            """

            def __init__(self, letter=None, freq=0, children=None):
                self.letter = letter
                self.freq = freq
                self.children = children or []

            def tuple(self):
                return (self.freq, ord(self.letter) if self.letter else -1)

            def __lt__(self, other):
                return self.tuple() < other.tuple()

            def __eq__(self, other):
                return self.tuple() == other.tuple()

        def encoding_table(node, code=''):
            """
            Превращает построенное алгоритмом Хаффмана дерево
            в словарь соответствия символ-код.
            """
            if node.letter is None:
                mapping = {}
                # Используем 0 и 1 для двоичного кодирования
                for child in node.children:
                    mapping.update(encoding_table(child, code + ('0' if child == node.children[0] else '1')))
                return mapping
            else:
                return {node.letter: code}

        def huffman_encode(text):
            """
            Кодирует строку текста алгоритмом Хаффмана с двоичным кодированием.
            :param text: текст для кодирования
            :return: tuple: (<дерево декодирования>, <закодированная строка>)
            """
            nodes = [Node(letter, freq) for letter, freq in Counter(text).items()]
            heapify(nodes)

            # Строит двоичное дерево
            while len(nodes) > 1:
                list_children = [heappop(nodes) for _ in range(2)]  # Всегда берём 2 элемента

                freq = sum([node.freq for node in list_children])
                node = Node(None, freq)
                node.children = list_children

                heappush(nodes, node)

            root = nodes[0]
            codes = encoding_table(root)

            return root, ''.join([codes[letter] for letter in text])

        # Пример использования функции
        tree, encoded_text = huffman_encode(text)

        return Response({"doc_name": doc_name, "Huffman_text": encoded_text})
