from oscar.apps.analytics.models import *  # noqa

ProductRecord._meta.get_field('score').db_index = True
