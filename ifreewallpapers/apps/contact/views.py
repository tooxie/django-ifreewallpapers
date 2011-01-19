# coding=UTF-8
from sendmail import send
from utils.decorators import render_response
from contact.forms import ContactForm
from contact.email import send_contact_email
to_response = render_response('contact/')

@to_response
def contact(request):
    contact = ContactForm()
    if request.method == "POST":
        post = request.POST.copy()
        if send_contact_email(post):
            return HttpResponseRedirect(reverse('contact_email_sent'))
        else:
            return HttpResponseRedirect(reverse('contact_email_error'))
    return 'form.html', {'form': contact}
