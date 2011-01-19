# coding=UTF-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.contrib import admin

# Create your models here.
class Subject(models.Model):
    name = models.CharField(_(u'Nombre'), max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    position = models.PositiveIntegerField(_(u'Posición'), default=1)
    inline = models.BooleanField(_(u'¿Mostrar las preguntas y respuestas en la misma página?'))
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return self.name

    def save(self):
        if not self.slug:
            from django.template.defaultfilters import slugify
            self.slug = slugify(self.name)
        super(Subject, self).save()

    class Meta:
        ordering = ['position', 'name']

    class Admin:
        pass

class Answer(models.Model):
    text = models.TextField(_(u'Respuesta'))

    def __unicode__(self):
        if len(self.text) > 50:
            return '%s...' % self.text[0:50]
        else:
            return self.text

    class Admin:
        pass

class Question(models.Model):
    text = models.CharField(_(u'Pregunta'), max_length=255)
    page = models.ForeignKey(FlatPage, blank=True, null=True)
    inline = models.BooleanField(_(u'¿Mostrar respuestas en la misma página?'))
    answer = models.ForeignKey(Answer, related_name="questions", blank=True, null=True)
    url = models.CharField(_(u'Vínculo'), max_length=255, blank=True, null=True)
    subject = models.ForeignKey(Subject, related_name="questions")
    position = models.PositiveIntegerField(_(u'Posición'), default=1)

    def __unicode__(self):
        return self.text

    def get_href(self):
        from django.template.defaultfilters import slugify
        if self.inline or self.answer:
            return '#%s' % slugify(self.text)
        if self.page:
            return self.page.url
        if self.url:
            return self.url
        return ''
    href=property(get_href)

    def get_answer(self):
        from django.contrib.markup.templatetags.markup import textile
        if self.answer:
            return textile(self.answer.text)
        if self.page:
            return textile(self.page.content)
    answer_text=property(get_answer)

    class Meta:
        ordering = ['position']

    class Admin:
        pass

admin.site.register(Subject)
admin.site.register(Answer)
admin.site.register(Question)
