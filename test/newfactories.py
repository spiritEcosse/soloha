import warnings

from test.factories.address import *  # noqa
from test.factories.basket import *  # noqa
from test.factories.catalogue import *  # noqa
from test.factories.contrib import *  # noqa
from test.factories.customer import *  # noqa
from test.factories.offer import *  # noqa
from test.factories.order import *  # noqa
from test.factories.partner import *  # noqa
from test.factories.payment import *  # noqa
from test.factories.utils import *  # noqa
from test.factories.voucher import *  # noqa

message = (
    "Module '%s' is deprecated and will be removed in the next major version "
    "of django-oscar"
) % __name__

warnings.warn(message, PendingDeprecationWarning)
