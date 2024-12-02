from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def login(request):

    user = get_object_or_404(User, email=request.data['email'])

    
    # .check_password compara un string con un hash, retorna True o False
    # SI LA COMPARACION DA FALSE, LOS DATOS INGRESADOS SON ERRONEOS(400)
    if not user.check_password(request.data['password']):
        return Response({"error:" "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

    # token, Boolean = Token.objects...
    token, created = Token.objects.get_or_create(user=user)

    # convertir estos datos del usuario en un diccionario , 
    # usamos el serializer, para convertir en json
    serializedData = UserSerializer(instance=user)
    
    return Response({"token": token.key, "user":serializedData.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):

    serializer = UserSerializer(data=request.data)

    # print("-----serializer-----")
    # print(serializer)
    # print("-----serializer-----")

    if serializer.is_valid():
        with transaction.atomic():
            # Se inicia una transacción atómica para asegurar que las operaciones
            # de la base de datos sean consistentes.

            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            user = serializer.save()
            token = Token.objects.create(user=user)

            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
#aqui se valida que en cada consulta,en el header, se envie el token)
def profile(request):
    print(request.user)

    return Response("You are logged with {} ".format(request.user.username), status=status.HTTP_200_OK)