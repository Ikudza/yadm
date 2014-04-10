"""
Base classes for build database fields.
"""

from yadm.markers import AttributeNotSet, NoDefault


class FieldDescriptor(object):
    """ Base desctiptor for fields
    """
    def __init__(self, name, field):
        self.name = name
        self.field = field
        self.default = field.default

    def __get__(self, instance, owner):
        if instance is not None:
            if self.name not in instance.__data__:
                instance.__data__[self.name] = self.field.default

            value = instance.__data__[self.name]

            if value is AttributeNotSet or value is NoDefault:
                raise AttributeError(self.name)

            elif hasattr(self.field, 'from_mongo'):
                return self.field.from_mongo(instance, value)

            else:
                return value

        else:
            return self

    def __set__(self, instance, value):
        if not isinstance(instance, type):
            value = self.field.prepare_value(value)

            if value != instance.__data__.get(self.name):
                instance.__fields_changed__.add(self.name)

            instance.__data__[self.name] = value

        else:
            setattr(instance, self.name, value)

    def __delete__(self, instance):
        if not isinstance(instance, type):
            setattr(instance, self.name, AttributeNotSet)


class Field(object):
    """ Base field for all batabase fields

    .. py:attribute:: descriptor_class

        Class of desctiptor for work with field

    .. py:attribute:: default (NoDefault)

        Default value. It is processed by ``prepare_value`` in the creating document
    """

    descriptor_class = FieldDescriptor
    default = NoDefault

    def __init__(self, default=NoDefault):
        if default is not NoDefault:
            self.default = self.prepare_value(default)

    def contribute_to_class(self, document_class, name):
        """ Add field for document_class

        :param MetaDocument document_class: document class for add
        """
        self.name = name
        self.document_class = document_class
        self.document_class.__fields__[name] = self
        setattr(document_class, name, self.descriptor_class(name, self))

    def prepare_value(self, value):
        """ The method is called when value is assigned for the attribute

        :param value: raw value
        :return: prepared value

        It must be accept one argument and return processed (e.g. casted) analog.
        Also it is called for the default value in the creating (not instance!)
        document.
        """
        return value
