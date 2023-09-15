from django.contrib import admin
from .models import Recipient


class RecipientAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "call_status",
        "last_updated_by",
        "created_at",
        "done_at",
    )
    list_filter = ("created_at", "done_at", "call_status")
    list_editable = ("call_status",)

    def get_queryset(self, request):
        """Limit entries based on status and user.""" ""
        qs = super().get_queryset(request)

        # If the user is superuser, he can see all entries
        if request.user.is_superuser:
            return qs.exclude(call_status="waiting")
        # Otherwise, show records created or updated by the current user
        else:
            return qs.filter(last_updated_by=request.user).exclude(
                call_status="waiting"
            )


admin.site.register(Recipient, RecipientAdmin)
