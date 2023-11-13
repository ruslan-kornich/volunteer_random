from django import forms


class CallbackForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=[("done", "Done"), ("refused", "Dont Want"), ("call_back", "Call Back")]
    )
    recipient_id = forms.IntegerField(widget=forms.HiddenInput())


class DateSelectForm(forms.Form):
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
