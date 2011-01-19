# coding=UTF-8
from django.forms import Form, CharField, EmailField, Textarea

class ContactForm(Form):
    name = CharField()
    email = EmailField()
    message = CharField(widget=Textarea())
