import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

import confu.schema
import confu.config

# Create your models here.


class Config(models.Model):

    """
    Config storage for django model instances

    Related to a django model instace through a generic
    foreign key relationship
    """

    # describes the relationship to the object
    # holding the config

    holder_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    holder_id = models.PositiveIntegerField()
    holder  = GenericForeignKey('holder_content_type', 'holder_id')

    # config data is stored seralized as JSON

    data = models.TextField(default="{}")

    class Meta:
        db_table = "confu_config"
        unique_together = [["holder_content_type", "holder_id"]]


    @property
    def config(self):

        """
        return a confu Config instance
        with generated defaults and validated
        against the schema specified in the model
        holding the config
        """

        if hasattr(self, "_config"):
            return self._config

        config = confu.config.Config(
            self.holder.schema,
            data = json.loads(self.data)
        )

        # apply defaults and validate
        config.data

        self._config = config

        return self._config


    def clean(self):

        """
        Checks the config was validated
        successfully against the confu schema and raises
        validation errors if not

        Also sets self.data to json serialized representation
        of the config
        """

        if self.config.errors:
            raise models.ValidationError({
                "config": [
                    f"{error}" for error in self.config.errors
                ]
            })

        self.data = self.config.json


class SaveConfigContext:

    """
    Context to use for updating and persisting changes
    to an object's config
    """

    def __init__(self, model_instance):
        self.model_instance = model_instance
        self.data = self.model_instance.config
        self.config_instance = self.model_instance.config_instance

    def __enter__(self):
        return self.data

    def __exit__(self, type, value, traceback):
        self.config_instance._config = confu.config.Config(
            self.model_instance.schema,
            data=self.data
        )
        self.model_instance.config_instance.full_clean()
        self.model_instance.config_instance.save()


class ConfuMixin:

    """
    Set this mixin class on any django model class that
    you want to have a confu config

    Either specify the confu schema by setting a class property
    called `Config` to a confu Schema class or override the
    the `schema` property method to return a confu Schema instance
    """

    @property
    def schema(self):

        """
        Returns a confu Schema instance to use for the
        model's config

        Override this to specify what schema to use
        """

        if hasattr(self, "Config"):
            return self.Config()
        raise NotImplementedError("Either override this return a schema instance or define a `Config` meta class for the schema")

    @property
    def config_instance(self):

        """
        Returns the Config object (django model instance) for
        this instance
        """

        if not hasattr(self, "_config"):
            content_type = ContentType.objects.get_for_model(self._meta.model)
            config, created = Config.objects.get_or_create(
                holder_content_type = content_type,
                holder_id = self.id
            )
            self._config = config
        return self._config

    @property
    def config(self):

        """
        Returns the config dict for this instance
        """

        return self.config_instance.config.data

    def update_config(self):
        """
        Returns context for updating, validating and persisting
        config changes
        """
        return SaveConfigContext(model_instance=self)
