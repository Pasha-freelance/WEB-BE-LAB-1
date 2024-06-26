import uuid

from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from todo.models import Todo, Person
from todo.serializers import ToDoSerializer, PersonSerializer


class TodoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows todos to be viewed or edited.
    """
    queryset = Todo.objects.all()
    serializer_class = ToDoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows person to be viewed or edited.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


@swagger_auto_schema(method='post', request_body=PersonSerializer)
# AUTHENTICATION
@api_view(['POST'])
def register_user(request):
    serializer = PersonSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    person = get_object_or_404(Person, username=request.data.get('username'))

    if person.check_password(request.data.get('password')):
        return Response({
            "profileId": person.profileId,
            "birthdate": person.birthdate,
            "email": person.email,
            "username": person.username,
        }, status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_401_UNAUTHORIZED)


# TODOS
@api_view(['GET'])
def all_todos(request, profile_id):
    owner = get_object_or_404(Person, profileId=profile_id)
    result = []
    for todo in Todo.objects.filter(owner=owner):
        result.append({
            "identifier": todo.identifier,
            "description": todo.description,
            "deadline": todo.deadline
        })

    return JsonResponse({'result': result})


@swagger_auto_schema(method='post', request_body=ToDoSerializer)
@api_view(['POST'])
def add_todo(request, profile_id):
    owner = get_object_or_404(Person, profileId=profile_id)
    todo_item = Todo(
        identifier=str(uuid.uuid4()),
        description=request.data.get('description'),
        deadline=request.data.get('deadline'),
        owner=owner
    )

    todo_item.save()
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=ToDoSerializer)
@api_view(['POST'])
def edit_todo(request, identifier):
    try:
        todo = Todo.objects.get(identifier=identifier)
    except Todo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ToDoSerializer(todo, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def remove_todo(request, identifier):
    todo = Todo.objects.get(identifier=identifier)
    todo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
