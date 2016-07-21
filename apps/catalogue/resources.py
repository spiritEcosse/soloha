from import_export import widgets as import_export_widgets
from import_export import resources, fields
import functools
import widgets


class Field(fields.Field):

    def is_m2m_with_intermediate_object(self, obj):
        field, _, _, m2m = obj._meta.get_field_by_name(self.attribute)
        return m2m and field.rel.through._meta.auto_created is False

    def get_intermediate_model(self, obj):
        field = obj._meta.get_field_by_name(self.attribute)[0]
        IntermediateModel = field.rel.through
        from_field_name = field.m2m_field_name()
        from_field_name = 'primary'
        to_field_name = field.rel.to.__name__.lower()
        to_field_name = 'recommendation'
        return IntermediateModel, from_field_name, to_field_name

    def remove_old_intermediates(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = \
            self.get_intermediate_model(obj)
        imported_ids = set(import_obj.pk for import_obj in self.clean(data))
        related_objects = getattr(obj, self.attribute).all()
        for related_object in related_objects:
            if related_object.pk not in imported_ids:
                queryset = IntermediateModel.objects.filter(**{
                    from_field_name: obj,
                    to_field_name: related_object
                })
                queryset.delete()

    def ensure_current_intermediates_created(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = \
            self.get_intermediate_model(obj)

        for related_object in self.clean(data):
            attributes = {from_field_name: obj, to_field_name: related_object}
            self.create_if_not_existing(IntermediateModel, attributes)

    @staticmethod
    def create_if_not_existing(IntermediateModel, attributes):
        # Use this instead of get_or_create in case we have duplicate
        # associations. (get_or_create would raise a DoesNotExist exception)
        if not IntermediateModel.objects.filter(**attributes).exists():
            IntermediateModel.objects.create(**attributes)

    def save(self, obj, data):
        """
        Cleans this field value and assign it to provided object.
        """
        self.widget.rel = obj._meta.get_field_by_name(self.attribute)[0].rel

        if not self.readonly:
            if self.is_m2m_with_intermediate_object(obj):
                self.remove_old_intermediates(obj, data)
                self.ensure_current_intermediates_created(obj, data)
            else:
                setattr(obj, self.attribute, self.clean(data))

    def export(self, obj):
        """
        Returns value from the provided object converted to export
        representation.
        """
        value = self.get_value(obj)
        if value is None:
            return ""
        if isinstance(self.widget, widgets.IntermediateModelManyToManyWidget):
            return self.widget.render(value, obj)
        else:
            return self.widget.render(value)


class ModelResource(resources.ModelResource):

    @classmethod
    def widget_from_django_field(cls, f, default=import_export_widgets.Widget):
        """
        Returns the widget that would likely be associated with each
        Django type.
        """
        result = default
        internal_type = f.get_internal_type()
        if internal_type in ('ManyToManyField', ):
            result = functools.partial(widgets.IntermediateModelManyToManyWidget,
                                       model=f.rel.to, rel=f.rel)
        if internal_type in ('ForeignKey', 'OneToOneField', ):
            result = functools.partial(import_export_widgets.ForeignKeyWidget,
                                       model=f.rel.to)
        if internal_type in ('DecimalField', ):
            result = import_export_widgets.DecimalWidget
        if internal_type in ('DateTimeField', ):
            result = import_export_widgets.DateTimeWidget
        elif internal_type in ('DateField', ):
            result = import_export_widgets.DateWidget
        elif internal_type in ('IntegerField', 'PositiveIntegerField',
                               'PositiveSmallIntegerField',
                               'SmallIntegerField', 'AutoField'):
            result = import_export_widgets.IntegerWidget
        elif internal_type in ('BooleanField', 'NullBooleanField'):
            result = import_export_widgets.BooleanWidget
        return result


    @classmethod
    def field_from_django_field(self, field_name, django_field, readonly):
        """
        Returns a Resource Field instance for the given Django model field.
        """

        FieldWidget = self.widget_from_django_field(django_field)
        widget_kwargs = self.widget_kwargs_for_field(field_name)
        field = Field(attribute=field_name, column_name=field_name,
                      widget=FieldWidget(**widget_kwargs), readonly=readonly)
        return field