from django.db import models
from django.db.models.query import QuerySet


class BaseQuerySet(QuerySet):

    def delete(self):
        super(BaseQuerySet, self).update(**{'trashed': True})


class BaseModelManager(models.Manager):

    def __init__(self):
        super(BaseModelManager, self).__init__()

    def get_queryset(self):
        return BaseQuerySet(model=self.model).filter(trashed=False)


class BaseModelManagerAll(models.Manager):

    def __init__(self):
        super(BaseModelManagerAll, self).__init__()

    def get_queryset(self):
        return BaseQuerySet(model=self.model)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trashed = models.BooleanField(default=False, db_index=True)

    objects = BaseModelManager()
    all_objects = BaseModelManagerAll()

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        forced_delete = kwargs.pop('forced', False)
        if forced_delete:
            super(BaseModel, self).delete(**kwargs)
        else:
            self.trashed = True
            self.save()

