from django.utils.timezone import localtime
from .models import Recipient
from django.utils import timezone
from django.http import HttpResponse
from django.core.paginator import Paginator
from datetime import date
from django.db import transaction

from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import CallbackForm


@login_required
def index(request):
    recipient = None
    current_user = request.user
    action_type = (
        request.POST.get("action_type", None) if request.method == "POST" else None
    )
    recipient_id = request.POST.get("recipient_id", None) if action_type else None

    if action_type and recipient_id:
        recipient = get_object_or_404(Recipient, pk=recipient_id)

    if request.method == "POST" and action_type:
        if action_type == "get_number":
            # Query for a new recipient
            recipients_waiting = Recipient.objects.filter(call_status="waiting")
            recipient = recipients_waiting.order_by("?").first()
            if recipient:
                request.session["last_recipient_id"] = recipient.id

        elif action_type in ["contacted", "callback", "refused", "invalid_number"]:
            # Change call_status based on action_type
            status_map = {
                "contacted": "done",
                "callback": "call_back",
                "refused": "refused",
                "invalid_number": "invalid",
            }
            recipient.call_status = status_map[action_type]
            recipient.done_at = localtime(
                timezone.now()
            )  # update every time the status changes

            # Update the timestamp if the status is changed to "done"
            if action_type == "contacted":
                recipient.done_at = localtime(timezone.now())
                print(recipient.done_at)

            # Update other fields if necessary
            if action_type == "callback":
                recipient.call_back_time = datetime.now() + timedelta(hours=2)

            recipient.last_updated_by = current_user
            recipient.save()

            if "last_recipient_id" in request.session:
                del request.session["last_recipient_id"]

        return redirect("index")

    else:  # GET request
        if "last_recipient_id" in request.session:
            recipient = Recipient.objects.filter(
                pk=request.session["last_recipient_id"], call_status="waiting"
            ).first()
            if not recipient:
                del request.session["last_recipient_id"]

    return render(request, "call_manager/index.html", {"recipient": recipient})


@login_required
def done_calls(request):
    if request.user.is_superuser:
        # If the user is superuser, we will show all completed calls
        recipients_list = Recipient.objects.filter(call_status="done").order_by(
            "-done_at"
        )
    else:
        # Otherwise, we will only show calls that have been updated by this user
        recipients_list = Recipient.objects.filter(
            call_status="done", last_updated_by=request.user
        ).order_by("-done_at")

    paginator = Paginator(recipients_list, 10)  # Покажем 10 записей на страницу

    page = request.GET.get("page")
    recipients = paginator.get_page(page)

    return render(request, "call_manager/done_calls.html", {"recipients": recipients})


@transaction.atomic
def callback_view(request):
    if request.method == "POST":
        form = CallbackForm(request.POST)

        if form.is_valid():
            recipient_id = form.cleaned_data["recipient_id"]
            new_status = form.cleaned_data["new_status"]

            recipient = get_object_or_404(Recipient, pk=recipient_id)

            if new_status == "done":  # Value for the "Contacted" button
                recipient.call_status = "done"
            elif new_status == "refused":  # The value for the "Don't Want" button
                recipient.call_status = "refused"
            elif (
                new_status == "callback"
            ):  # If the "Call Back" button should also change status
                recipient.call_status = "call_back"

            # Set the status update time for all cases
            recipient.done_at = localtime(timezone.now())

            recipient.last_updated_by = request.user
            recipient.save()

            return redirect("callback_view")
        else:
            print(form.errors)
            return HttpResponse(f"Error in the form: {form.errors}", status=400)
    # If the user is a superuser, show all callback numbers
    if request.user.is_superuser:
        callback_numbers = Recipient.objects.filter(
            call_status="call_back", call_back_time__isnull=False
        ).select_related("last_updated_by")
    else:
        # Otherwise, show only the numbers that have been updated by this user
        callback_numbers = Recipient.objects.filter(
            last_updated_by_id=request.user.id,
            call_status="call_back",
            call_back_time__isnull=False,
        ).select_related("last_updated_by")

    data = [
        {
            "phone_number": number.phone_number,
            "call_back_time": localtime(number.call_back_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "updated_by": number.last_updated_by.username,
            "done_at": localtime(number.done_at).strftime("%H:%M %d.%m.%Y")
            if number.done_at
            else None,
            "form": CallbackForm(initial={"recipient_id": number.id}),
            "recipient": number,
        }
        for number in callback_numbers
    ]

    context = {"callback_numbers": data}
    return render(request, "call_manager/callback.html", context)


@login_required
def statistic_view(request):
    # Define the base query
    base_query = Recipient.objects.all()

    if not request.user.is_superuser:
        # If this is not a superuser, limit the query to only those records belonging to this user
        base_query = base_query.filter(last_updated_by_id=request.user.id)

    # General Statistics
    done_calls = base_query.filter(call_status="done").count()
    callbacks = base_query.filter(call_status="call_back").count()
    invalid_numbers = base_query.filter(call_status="invalid").count()
    refused_calls = base_query.filter(call_status="refused").count()

    # Today's statistics
    today = date.today()
    done_calls_today = base_query.filter(
        call_status="done", created_at__date=today
    ).count()
    callbacks_today = base_query.filter(
        call_status="call_back", created_at__date=today
    ).count()
    invalid_numbers_today = base_query.filter(
        call_status="invalid_number", created_at__date=today
    ).count()
    refused_calls_today = base_query.filter(
        call_status="refused", created_at__date=today
    ).count()

    context = {
        "done_calls": done_calls,
        "callbacks": callbacks,
        "invalid_numbers": invalid_numbers,
        "refused_calls": refused_calls,
        "done_calls_today": done_calls_today,
        "callbacks_today": callbacks_today,
        "invalid_numbers_today": invalid_numbers_today,
        "refused_calls_today": refused_calls_today,
    }
    return render(request, "call_manager/statistic.html", context)
