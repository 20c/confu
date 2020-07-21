from django.db import models

from confu.db.django.confu.models import ConfuMixin
from confu.schema import *

class ServerConfig(Schema):

    address = IpAddress(default="127.0.0.1")
    port = Int(default=80)

class Server(ConfuMixin, models.Model):

    name = models.CharField(max_length=255)

    @property
    def schema(self):
        return ServerConfig()
