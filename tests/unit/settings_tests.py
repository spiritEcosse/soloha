from django.test import TestCase
from django.template import loader, Context, TemplateDoesNotExist

import soloha


class TestsolohaCoreAppsList(TestCase):

    def test_includes_soloha_itself(self):
        core_apps = soloha.soloha_CORE_APPS
        self.assertTrue('soloha' in core_apps)

    def test_can_be_retrieved_through_fn(self):
        core_apps = soloha.get_core_apps()
        self.assertTrue('soloha' in core_apps)

    def test_can_be_retrieved_with_overrides(self):
        apps = soloha.get_core_apps(overrides=['apps.shipping'])
        self.assertTrue('apps.shipping' in apps)
        self.assertTrue('apps.shipping' not in apps)

    def test_raises_exception_for_string_arg(self):
        with self.assertRaises(ValueError):
            soloha.get_core_apps('forks.catalogue')


class TestsolohaTemplateSettings(TestCase):
    """
    soloha's soloha_MAIN_TEMPLATE_DIR setting
    """
    def test_allows_a_template_to_be_accessed_via_two_paths(self):
        paths = ['base.html', 'soloha/base.html']
        for path in paths:
            try:
                loader.get_template(path)
            except TemplateDoesNotExist:
                self.fail("Template %s should exist" % path)

    def test_allows_a_template_to_be_customized(self):
        path = 'base.html'
        template = loader.get_template(path)
        rendered_template = template.render(Context())
        self.assertIn('soloha Test Shop', rendered_template)

    def test_default_soloha_templates_are_accessible(self):
        path = 'soloha/base.html'
        template = loader.get_template(path)
        rendered_template = template.render(Context())
        self.assertNotIn('soloha Test Shop', rendered_template)
