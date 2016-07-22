from django.db import models


def shift_paths(exclude, name):
    return tuple(item.split('.', 1)[1] for item in exclude
                 if item.startswith(('{0}.'.format(name), '*.')))


def deep_dump_instance(instance,
                       depth=1,
                       exclude=(),
                       include=(),
                       order_by=(),
                       seen=None):
    """Deep-dumps fields of a model instance as (name, value) tuples

    Examples::

        # create a fixture
        >>> my_poll = Poll.objects.create(question=u"What's up?",
                                          pub_date=datetime.datetime.now())
        >>> choice_1 = my_poll.choice_set.create(choice='Not much', votes=5)
        >>> choice_2.choice_set.create(choice='The sky', votes=2)

        # recurse all related objects
        >>> deep_dump_instance(my_poll)
        [('question', u"What's up?"),
         ('pub_date', datetime.datetime(2012, 1, 30, 9, 48)),
         ('choice_set',
          [[('choice', u'Not much'), ('votes', 5)],
           [('choice', u'The sky'), ('votes', 2)]])]

        # skip all related objects
        >>> deep_dump_instance(my_poll, depth=0)
        [('question', u"What's up?"),
         ('pub_date', datetime.datetime(2012, 1, 30, 9, 48))]

        # exclude a field
        >>> deep_dump_instance(my_poll, exclude=['pub_date'])
        [('question', u"What's up?"),
         ('choice_set',
          [[('choice', u'Not much'), ('votes', 5)],
           [('choice', u'The sky'), ('votes', 2)]])]

        # only include a field in related objects
        >>> deep_dump_instance(choice_1,
        ...                    exclude=['*', 'question.*'],
        ...                    include=['poll', 'poll.pub_date'])
        [[('poll',
          [('pub_date', datetime.datetime(2012, 1, 30, 9, 48))])]]

        # sort related objects
        >>> deep_dump_instance(my_poll,
        ...                    exclude=['*'],
        ...                    include=['choice_set'],
        ...                    order_by=['choice_set.votes'])
        [('choice_set',
          [[('choice', u'The sky'), ('votes', 2)],
           [('choice', u'Not much'), ('votes', 5)]])]

    """
    if not seen:
        seen = set()
    if (instance.__class__, instance.pk) in seen:
        return '<recursive>'
    seen.add((instance.__class__, instance.pk))
    field_names = sorted(
        [field.name for field in instance._meta.fields] +
        [f.get_accessor_name() for f in instance._meta.get_all_related_objects()])

    dump = []
    exclude_all = '*' in exclude
    for name in field_names:
        if name in include or (not exclude_all and name not in exclude):
            try:
                value = getattr(instance, name)
            except models.ObjectDoesNotExist:
                value = None
            if value.__class__.__name__ == 'RelatedManager':
                if depth >= 1:
                    related_objects = value.all()
                    for ordering in order_by:
                        parts = ordering.split('.')
                        if len(parts) == 2 and parts[0] == name:
                            related_objects = related_objects.order_by(parts[1])
                    value = [deep_dump_instance(related,
                                                depth=depth - 1,
                                                exclude=shift_paths(exclude, name),
                                                include=shift_paths(include, name),
                                                order_by=shift_paths(order_by, name),
                                                seen=seen)
                             for related in related_objects]
                else:
                    continue
            elif isinstance(value, models.Model):
                if depth >= 1:
                    value = deep_dump_instance(value,
                                               depth=depth - 1,
                                               exclude=shift_paths(exclude, name),
                                               include=shift_paths(include, name),
                                               order_by=shift_paths(order_by, name),
                                               seen=seen)
                else:
                    continue
            dump.append((name, value))
    return dump