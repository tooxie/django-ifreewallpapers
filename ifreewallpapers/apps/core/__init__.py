from core.models import Wallpaper
from rating.models import RatedItem
import tagging

tagging.register(Wallpaper)
setattr(Wallpaper, 'rating', RatedItem.objects)
