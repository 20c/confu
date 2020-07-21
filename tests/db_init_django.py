import os



BASE_DIR = os.path.dirname(__file__)

def init():

    # only setup django if django is installed
    # in the testing environment

    try:
        from django.conf import settings
    except ImportError:
        return

    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "confu.db.django.confu",
            "confu.db.django.confu_test",
        ],
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(BASE_DIR, 'django-test.sqlite3')
            }
        }
    )
