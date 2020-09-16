from rest_framework import serializers
from invite.models import Invite
from django.template import loader
from base.tasks import send_email
from utils import constants


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ('id', 'created_at', 'email', 'first_name', 'last_name', 'role')

    def create(self, validated_data):
        admin = self.context['request'].user
        recipient_email = self.validated_data['email']
        validated_data['admin'] = admin
        invite = super().create(validated_data)
        context = {
            'admin_name': admin.first_name,
            'organization_name': admin.organization.name,
            'invite_id': invite.key
        }
        html_message = loader.get_template('invite.html').render(context)
        send_email.delay(html_message=html_message, recipient_email=recipient_email, subject=constants.SUBJECT_INVITATION)
        return invite
