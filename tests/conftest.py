import tests.db_init_django

def pytest_configure():
    tests.db_init_django.init()
