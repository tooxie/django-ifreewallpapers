from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
# from favorites.managers import FavoriteManager

class Favourite(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    object = generic.GenericForeignKey()
    user = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)
    
    # objects = FavoriteManager

    def __unicode__(self):
        return _(u'%(object)s for %(user)s') % \
                {'object': self.object, 'user': self.user.username}

    def toggle(self):
        if self.id:
            # print 'deleting...', self.id
            self.delete()
        else:
            # print 'getting id...',
            self.save()
            # print self.id
        return True

