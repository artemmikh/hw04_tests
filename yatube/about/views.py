from django.views.generic.base import TemplateView


class AboutTechView(TemplateView):
    template_name = 'posts/about/tech.html'
