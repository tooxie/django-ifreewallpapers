# -*- coding: utf-8 -*-
# Thanks to gonz
from os.path import abspath, basename, dirname, join
import sys

PROJECT_ABSOLUTE_DIR = dirname(abspath(__file__))
PROJECT_NAME = basename(PROJECT_ABSOLUTE_DIR)

# Add apps/ dir to python path.
apps = join(PROJECT_ABSOLUTE_DIR, "apps")
if apps not in sys.path:
    sys.path.insert(0, apps)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.comments',

    'blog',
    'core',
    'faq',
    'favs',
    'friends',
    'limbo',
    'menuse',
    'messaging',
    # 'multilingual',
    'notification',
    'profile',
    'rating',
    'sendmail',
    'tagging',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

    'apps.debug.footer.DebugFooter',
    'utils.middleware.spaceless.SpacelessMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'context_processors.language',
    'context_processors.urls',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

LANGUAGES = (
  ('es', 'Español'),
  ('en', 'English'),
)
LANGUAGE_CODE = 'en-us'
DEFAULT_LANGUAGE = 1

DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

SECRET_KEY = '+h7%#*o!3^ko2_^4ZA27#.,a.,N^^7s7s7^(CRGL&&^5lax1&sw(uuf'

ROOT_URLCONF = '%(project)s.urls.%(lang)s' % \
              {'project': PROJECT_NAME, 'lang': LANGUAGE_CODE[:2]}

# MEDIA
PROJECT_ABSOLUTE_DIR = dirname(abspath(__file__))
MEDIA_ROOT = PROJECT_ABSOLUTE_DIR + '/media/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
UPLOAD_DIR = MEDIA_ROOT + 'wallpapers/'
ORPHANS_DIR = MEDIA_ROOT + 'orphans/'
BACKUP_DIR = PROJECT_ABSOLUTE_DIR + '/backups/'

WATERMARK_FILE = UPLOAD_DIR + 'watermark.png'
ALLOWED_CONTENT_TYPES = (
    ('image/png', 'png'),
    ('image/x-png', 'png'),  # IE hack. I hate you.
    ('image/gif', 'gif'),
    ('image/jpeg', 'jpg'),
    ('image/pjpeg', 'jpg'),  # IE hack. I hate you.
    # ('image/tiff', 'tiff'),
    # ('image/x-ms-bmp', 'bmp'),
    # ('image/svg+xml', 'svg'),
)
ALLOWED_IMAGE_SIZE = 10*1024 # 10MB = 10240KB
VALIDATOR_USER_AGENT = """Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.4) \
Gecko/2008112309 Iceweasel/3.0.4 (Debian-3.0.4-1)"""

IMG_URL = '%simg/' % MEDIA_URL
CSS_URL = '%scss/' % MEDIA_URL
JS_URL = '%sjs/' % MEDIA_URL

# TEMPLATES
TEMPLATE_DIRS = (
    join(PROJECT_ABSOLUTE_DIR, 'templates'),
)
ADMIN_TEMPLATE_DIRS = (
    join(PROJECT_ABSOLUTE_DIR, 'templates'),
)
FIXTURE_DIRS = (
    join(PROJECT_ABSOLUTE_DIR, 'fixtures'),
)
AUTH_PROFILE_MODULE='profile.profile'

# EMAIL
EMAIL_HOST_PORT = 25
EMAIL_USE_TLS = False
EMAIL_FAIL_SILENTLY = False
EMAIL_SIGNATURE_TEMPLATE = 'signature.txt'
EMAIL_CLAVE_TEMPLATE = 'clave.txt'
EMAIL_TELL_A_FRIEND_TEMPLATE = 'tellafriend.txt'
EMAIL_RECOVER_PASSWORD = 'recover.txt'

# tagging
FORCE_LOWERCASE_TAGS = True

# Override previous settings with values in local_settings.py settings file.
try:
    from local_settings import *
except ImportError:
    debug_msg ="Can't find local_settings.py, using default settings."
    try:
        from mod_python import apache
        apache.log_error("%s" % debug_msg, apache.APLOG_NOTICE)
    except ImportError:
        import sys
        sys.stderr.write("%s\n" % debug_msg)
