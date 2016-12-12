import json

from django.utils.encoding import force_text

from import_export import widgets as widgets


class IntermediateModelManyToManyWidget(widgets.ManyToManyWidget):
    def __init__(self, *args, **kwargs):
        super(IntermediateModelManyToManyWidget, self).__init__(*args, **kwargs)
        self.rel_field = None
        self.intermediate_own_fields = []

    def clean(self, value):
        items = json.loads(value)
        for key, item in enumerate(items[:]):
            items[key][self.field] = self.model.objects.get(**{self.field: item[self.field]})
        return items

    def render(self, value, obj):
        return json.dumps([self.related_object_representation(obj, related_obj) for related_obj in value.all()])

    def related_object_representation(self, obj, related_obj):
        result = {self.field: getattr(related_obj, self.field, None)}

        if self.rel_field.rel.through._meta.auto_created:
            return result

        intermediate_obj = self.rel_field.rel.through.objects.filter(**{
            self.rel_field.m2m_reverse_field_name(): related_obj,
            self.rel_field.m2m_field_name(): obj
        }).first()

        if intermediate_obj is not None:
            for field in self.intermediate_own_fields:
                result[field.name] = force_text(getattr(intermediate_obj, field.name))
        else:
            for field in self.intermediate_own_fields:
                result[field.name] = field.default if field.default else None

        return result


class CharWidget(widgets.Widget):
    """
    Widget for converting text fields.
    """

    def render(self, value):
        try:
            featured_value = force_text(int(float(value)))
        except ValueError:
            featured_value = force_text(value)
        return featured_value


class ForeignKeyWidget(widgets.ForeignKeyWidget):
    def clean(self, value):
        return super(ForeignKeyWidget, self).clean(value.strip())


class ManyToManyWidget(widgets.ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()

        ids = filter(None, value.split(self.separator))
        ids = map(lambda slug: slug.strip(), ids)
        return self.model.objects.filter(**{
            '%s__in' % self.field: ids
        })
