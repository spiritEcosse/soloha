from django.template import Library, Node, Variable
from django.template.loader import select_template
from django.template import RequestContext, Context


register = Library()


class PromotionNode(Node):
    def __init__(self, promotion):
        self.promotion_var = Variable(promotion)

    def render(self, context):
        promotion = self.promotion_var.resolve(context)
        template = select_template([promotion.template_name(), 'promotions/default.html'])
        args = {'promotion': promotion, 'request': context['request']}
        args.update(**promotion.template_context(request=context['request']))
        return template.render(Context(args))


def get_promotion_html(parser, token):
    _, promotion = token.split_contents()
    return PromotionNode(promotion)


register.tag('render_promotion', get_promotion_html)
