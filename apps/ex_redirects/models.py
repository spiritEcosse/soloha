from django.contrib.redirects.models import Redirect

Redirect._meta.get_field('old_path').max_length = 5000
Redirect._meta.get_field('new_path').max_length = 5000
