from django.contrib import admin
from .models import Recipient, CustomUser
from django.contrib.admin import SimpleListFilter, AdminSite
from django.http import HttpResponse
from openpyxl import Workbook


def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="recipients.xlsx"'

    wb = Workbook()
    ws = wb.active

    # Заголовки для колонок
    columns = [
        'Name', 'Phone Number', 'Items Received', 'Call Status',
        'State', 'Place', 'Date Distribution', 'Gender',
        'Age', 'Volunteer', 'Created At', 'Last Updated',
        'Done At', 'Last Updated By', 'Call Back Time'
    ]
    ws.append(columns)

    # Добавление данных
    for recipient in queryset:
        items_received = ', '.join([str(item) for item in recipient.items_received.all()])
        last_updated_by = recipient.last_updated_by.full_name if recipient.last_updated_by else 'Unknown'
        created_at = recipient.created_at.replace(tzinfo=None) if recipient.created_at else None
        last_updated = recipient.last_updated.replace(tzinfo=None) if recipient.last_updated else None
        done_at = recipient.done_at.replace(tzinfo=None) if recipient.done_at else None
        call_back_time = recipient.call_back_time.replace(tzinfo=None) if recipient.call_back_time else None

        row = [
            recipient.name, recipient.phone_number, items_received, recipient.call_status,
            recipient.state, recipient.place, recipient.date_distribution, recipient.gender,
            recipient.age, recipient.volunteer, created_at, last_updated,
            done_at, last_updated_by, call_back_time
        ]

        ws.append(row)

    wb.save(response)
    return response


export_to_excel.short_description = "Экспорт в Excel"

# Настройки для заголовков и названий в стандартной админ-панели
admin.site.site_header = "Call Manager Admin Portal"
admin.site.site_title = "Call Manager Admin Portal"
admin.site.index_title = "Welcome to Call Manager Admin Portal"


# Кастомный фильтр для админ-панели
class UserFilter(SimpleListFilter):
    title = "Last Updated By"
    parameter_name = "last_updated_by"

    def lookups(self, request, model_admin):
        users = CustomUser.objects.filter(is_superuser=False)
        # Чтобы избежать проблемы с None
        return [
            (user.id, user.full_name or user.username or "Unknown") for user in users
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(last_updated_by__id=self.value())


class RecipientAdmin(admin.ModelAdmin):
    actions = [export_to_excel]
    list_display = (
        "phone_number",
        "call_status",
        "get_full_name_of_last_updated_by",  # Новый метод для отображения полного имени
        "done_at",
        "created_at",
    )
    list_filter = (UserFilter, "call_status", "done_at")
    list_editable = ("call_status",)
    search_fields = ['phone_number', ]
    ordering = ("-done_at",)  # Сортировка по убыванию для поля done_at

    def get_full_name_of_last_updated_by(self, obj):
        if obj.last_updated_by:
            return obj.last_updated_by.full_name or obj.last_updated_by.username
        return "Unknown"

    get_full_name_of_last_updated_by.short_description = "Last Updated By"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.exclude(call_status="waiting")
        else:
            return qs.filter(last_updated_by=request.user).exclude(
                call_status="waiting"
            )


admin.site.register(Recipient, RecipientAdmin)


class RecipientModerationAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "call_status", "created_at")
    list_editable = ("call_status",)
    search_fields = ['phone_number', ]

    # Метод для отображения записей со статусом "waiting"
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(call_status="waiting")


# Новый AdminSite для модерации:
class ModerationAdminSite(AdminSite):
    site_header = "Moderation Admin"
    site_title = "Moderation Admin Portal"
    index_title = "Welcome to the Moderation Portal"


moderation_site = ModerationAdminSite(name="moderationadmin")

# Зарегистрировать модели с этим новым сайтом администратора:
moderation_site.register(Recipient, RecipientModerationAdmin)
