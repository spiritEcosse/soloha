from apps.customer.views import AccountSummaryView as solohaAccountSummaryView


class AccountSummaryView(solohaAccountSummaryView):
    # just here to test import in loading_tests:ClassLoadingWithLocalOverrideTests
    pass
