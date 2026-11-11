from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone

from .models import LeadDetails, Leads


class LeadDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadDetails
        fields = ('field_name', 'field_data')


class LeadsSerializer(serializers.ModelSerializer):
    details = LeadDetailsSerializer(source='leaddetails_set', many=True, read_only=True)
    executive_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    is_confused = serializers.SerializerMethodField()
    interview_email_sent = serializers.SerializerMethodField()
    send_channel = serializers.SerializerMethodField()

    class Meta:
        model = Leads
        fields = (
            'id', 'name', 'email', 'contact', 'source', 'added_date', 'added_time',
            'status', 'executive_name', 'category_name', 'client_name', 'details',
            'is_confused', 'interview_email_sent', 'send_channel',
        )

    def get_executive_name(self, obj):
        return obj.collected_by.name if obj.collected_by else ''

    def get_category_name(self, obj):
        return obj.lead_category.collection_for if obj.lead_category else ''

    def get_client_name(self, obj):
        if obj.lead_category and obj.lead_category.client_task and obj.lead_category.client_task.client:
            return obj.lead_category.client_task.client.client_name or ''
        if obj.work and obj.work.client:
            return obj.work.client.client_name or ''
        return ''

    def get_is_confused(self, obj):
        return bool(obj.is_confused)

    def get_interview_email_sent(self, obj):
        sent_entries = [detail for detail in obj.leaddetails_set.all() if detail.field_name == 'Interview Link Sent']
        if not sent_entries or not sent_entries[-1].field_data:
            return False
        try:
            raw = sent_entries[-1].field_data.strip()
            iso_str = raw.split(':', 1)[1] if raw.startswith(('sms:', 'email:')) else raw
            sent_at = datetime.fromisoformat(iso_str)
            if timezone.is_naive(sent_at):
                sent_at = timezone.make_aware(sent_at, timezone.get_current_timezone())
            return timezone.now() - sent_at < timedelta(minutes=10)
        except (TypeError, ValueError):
            return False

    def get_send_channel(self, obj):
        from .validators import is_valid_email, is_valid_phone
        from django.conf import settings
        has_email = is_valid_email(obj.email)
        has_phone = is_valid_phone(obj.contact)
        if has_phone and not has_email:
            return 'sms'
        if has_email and not has_phone:
            return 'email'
        if has_email and has_phone:
            return getattr(settings, 'INTERVIEW_PREFERRED_CHANNEL', 'email').lower()
        return None
