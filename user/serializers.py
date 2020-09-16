from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()

    def get_organization_id(self, obj):
        return obj.organization.id

    def get_organization_name(self, obj):
        return obj.organization.name

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'first_name',
            'last_name', 'role', 'date_of_birth',
            'profile_picture', 'phone', 'address', 'gender',
            'organization_id', 'organization_name', 'created_at'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):

        email = validated_data.get('email')
        password = validated_data.get('password')
        if email:
            validated_data.pop('email')
        if password:
            validated_data['password'] = make_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

