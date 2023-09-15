from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("done-calls/", views.done_calls, name="done_calls"),
    path("callback/", views.callback_view, name="callback_view"),
    path("statistic/", views.statistic_view, name="statistic_view"),
]
