from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.serializers import LoginSerializer, AuthTokenSerializer, SignupSerializer


class AuthView(viewsets.ViewSet):
    permission_classes_by_action = {'login': [AllowAny], 'logout': [IsAuthenticated], 'signup': [AllowAny]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @action(methods=['post'], detail=False)
    def login(self, request):
        login_serializer = LoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)

        user = login_serializer.validated_data['user']

        auth_token_serializer = AuthTokenSerializer(data={}, partial=True)
        auth_token_serializer.is_valid(raise_exception=True)
        auth_token_serializer.save(user=user)
        return Response(auth_token_serializer.data)

    @action(methods=['post'], detail=False)
    def logout(self, request):
        request.auth.delete()
        return Response()

    @action(methods=['post'], detail=True)
    @parser_classes([FormParser, MultiPartParser])
    def signup(self, request, pk):
        data = dict(request.data)
        '''
        request.data: A query dict (<QueryDict: {'email': ['kashish.sharma@joshtechnologygroup.com'],
         'password': ['qwerty123456789'], 'first_name': ['Kashish'],
          'last_name': ['Sharma'], 'phone': ['8130706991'], 'gender': ['1']}>)
        
        1. converting it to a dict
        
        data: {'email': ['kashish.sharma@joshtechnologygroup.com'], 'password': ['qwerty123456789'],
         'first_name': ['Kashish'], 'last_name': ['Sharma'], 'phone': ['8130706991'], 'gender': ['1']}
        
        2. Each element of a dictionary is list, converting to a standard dict and then passing to serializer
        
        '''
        for key in request.data:
            data[key] = data[key][0]
        signup_serializer = SignupSerializer(data=data, context={'invite_token': pk}, partial=True)
        signup_serializer.is_valid(raise_exception=True)
        signup_serializer.save()
        return Response(status=status.HTTP_201_CREATED)
