from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['name', 'description']

class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']