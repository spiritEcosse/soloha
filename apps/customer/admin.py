from django.contrib import admin
from apps.customer.models import CommunicationEventType, Email


admin.site.register(Email)
admin.site.register(CommunicationEventType)
