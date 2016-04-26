from haystack.forms import SearchForm


class ProductsSearchForm(SearchForm):

    def no_query_found(self):
        return None
        # return self.searchqueryset.all()
