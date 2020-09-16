from django.db.models import ObjectDoesNotExist
from rest_framework import serializers
from authentication.models import AuthToken
from user.models import User
from user.serializers import UserSerializer
from invite.models import Invite
from invite.exceptions import InvitationFailed, InvitationExpired
from base.token_expire_handler import is_token_expired
from rest_framework import exceptions
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.template import loader
from base.tasks import send_email
from utils import constants


class AuthTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AuthToken
        fields = ('created_at', 'key', 'user')


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    role = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'date_of_birth', 'first_name', 'last_name', 'role',
            'organization', 'profile_picture', 'phone', 'address', 'gender',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        try:
            invite_token = self.context.get('invite_token')
            invite = Invite.objects.select_related('admin', 'admin__organization').get(key=invite_token)
            is_expired = is_token_expired(invite)
            if is_expired:
                raise InvitationExpired
            admin = invite.admin
            validated_data['email'] = invite.email
            validated_data['password'] = make_password(validated_data['password'])
            validated_data['first_name'] = validated_data.get('first_name', invite.first_name)
            validated_data['last_name'] = validated_data.get('last_name', invite.last_name)
            validated_data['role'] = invite.role
            validated_data['organization'] = admin.organization
            instance = super().create(validated_data)
            invite.delete()
            recipient_email = invite.email
            context = {
                'organization_name': admin.organization.name
            }
            html_message = loader.get_template('welcome.html').render(context)
            send_email.delay(html_message=html_message, recipient_email=recipient_email, subject=constants.SUBJECT_WELCOME)
            return instance
        except ObjectDoesNotExist:
            raise InvitationFailed


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                data['user'] = user
            else:
                msg = constants.USER_DOES_NOT_EXISTS
                raise exceptions.ValidationError(msg)
        else:
            msg = constants.EMAIL_AND_PASSWORD_REQUIRED
            raise exceptions.ValidationError(msg)
        return data
