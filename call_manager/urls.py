from django.urls import path
from . import views
from call_manager.admin import moderation_site

urlpatterns = [
    path("", views.index, name="index"),
    path("done-calls/", views.done_calls, name="done_calls"),
    path("callback/", views.callback_view, name="callback_view"),
    path("statistic/", views.statistic_view, name="statistic_view"),
    path("personality/", views.call_statistics, name="superuser_statistics"),
    path("records/", moderation_site.urls),
]
