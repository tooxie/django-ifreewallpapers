# coding=UTF-8
from django.template import Library, Node, TemplateSyntaxError
from faq.models import Subject, Answer, Question
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

register = Library()

def render_subject_and_questions(subject_slug):
    try:
        subject = Subject.objects.get(slug=subject_slug)
    except:
        return ''
    html = '<h3 class="faq-title">%s</h3>' % subject
    html += '<ul class="faq-questions" id="%s">' % subject_slug
    for question in subject.questions.all():
        html += '<li class="%(class)s_question"><a href="%(href)s" title="%(title)s">%(text)s</a></li>' % { 'class': subject_slug, 'href': question.href, 'title': question.text, 'text': question.text }
    html += '</ul>'
    return html

class SubjectNode(Node):
    def __init__(self, subjects):
        self.subjects = subjects

    def render(self, context):
        html = ''
        for subject in self.subjects:
            html += render_subject_and_questions(subject)
        return html

class QuestionNode(Node):
    def render(self, context):
        try:
            subjects = Subject.objects.all()
            html = ''
            for subject in subjects:
                html += render_subject_and_questions(subject.slug)
        except Exception, e:
            print e
            html = ''
        return html

class AnswerNode(Node):
    def render(self, context):
        try:
            subjects = Subject.objects.all()
        except:
            return ''
        html = ''
        for subject in subjects:
            html += '<h3 class="faq-title">%s</h3>' % subject
            for question in subject.questions.all():
                html += '<h4 class="faq-question" id="%(id)s">%(title)s</h4>' % { 'id': slugify(question.text), 'title': question }
                html += '<div class="faq-answer">%(answer)s</div>' % { 'answer': question.answer_text }
        return html

def render_subject(parser, token):
    bits = token.contents.split()
    if len(bits) == 1:
        raise TemplateSyntaxError, _(u"render_subject recibe al menos un argumento, el nombre de uno o mas temas.")
    return SubjectNode(bits)

def render_questions(parser, token):
    bits = token.contents.split()
    if len(bits) != 1:
        raise TemplateSyntaxError, _(u"render_questions no recibe argumentos.")
    return QuestionNode()

def render_answers(parser, token):
    bits = token.contents.split()
    if len(bits) != 1:
        raise TemplateSyntaxError, _(u"render_answers no recibe argumentos.")
    return AnswerNode()

menu = register.tag(render_subject)
menu = register.tag(render_questions)
menu = register.tag(render_answers)
