from django.db.models import Model, DateTimeField, ForeignKey, \
                             PositiveIntegerField, BooleanField
from django.contrib.auth.models import User

from core import models as core

from datetime import datetime

class Wallpaper(Model):
    wallpaper = ForeignKey(core.Wallpaper, related_name='limbo')
    saves = PositiveIntegerField(default=0)
    dooms = PositiveIntegerField(default=0)

    def save_it(self, user):
        return self.__vote(user, True)

    def doom_it(self, user):
        return self.__vote(user, False)

    def __vote(self, user, save_it):
        try:
            my_decision = Decision.objects.get(judge=user, wallpaper=self)
            return False
        except:
            my_decision = Decision(judge=user, wallpaper=self, save_it=save_it)

        # ### Saving algorithm ### #
        if Decision.objects.count(wallpaper=self, save_it=True) >= 10:
            self.wallpaper.forgiven = True
            self.wallpaper.save()
            self.wallpaper.ping_google()
        # ### ################ ### #

        return True

    def voted_by(self, user):
        return bool(Decision.objects.filter(
            wallpaper=self, judge=user).count())


class Decision(Model):
    wallpaper = ForeignKey(Wallpaper, related_name='votes')
    save_it = BooleanField()
    judge = ForeignKey(User)
    date = DateTimeField()
    saved_on = DateTimeField(blank=True, null=True)

    def save(self):
        if not self.id:
            self.date = datetime.now()
        super(Decision, self).save()

    class META:
        unique_together = ('wallpaper', 'judge')
