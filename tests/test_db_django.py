import pytest
import ipaddress

pytest.importorskip("django")

from confu.db.django.confu_test.models import (
    Server
)

@pytest.mark.django_db
def test_models():

    # create Server instance
    server = Server.objects.create(name="test")

    # check config default value
    assert server.config["address"] == ipaddress.ip_address("127.0.0.1")

    # update config (this also validates)
    with server.update_config() as config:
        config.update(address="192.168.1.1")

    # reload the server object
    server = Server.objects.all().first()

    # assert that the update was saved
    assert server.config["address"] == ipaddress.ip_address("192.168.1.1")
