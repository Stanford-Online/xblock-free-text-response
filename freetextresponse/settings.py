"""
Settings for freetextresponse xblock
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': 'intentionally-omitted',
    },
}
INSTALLED_APPS = (
    'freetextresponse',
)
LOCALE_PATHS = [
    'freetextresponse/translations',
]
SECRET_KEY = 'SECRET_KEY'
