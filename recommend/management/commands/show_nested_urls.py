from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver
from django.utils.text import capfirst

class Command(BaseCommand):
    help = 'Displays all URLs in the project, including nested ones'

    def handle(self, *args, **kwargs):
        resolver = get_resolver()
        self.print_urls(resolver.url_patterns, '')

    def print_urls(self, patterns, prefix):
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # Direct URL pattern
                self.stdout.write(f"{prefix}{pattern.pattern} -> {pattern.callback.__module__}.{pattern.callback.__name__}")
            elif isinstance(pattern, URLResolver):
                # Nested URL resolver (e.g., include())
                self.stdout.write(f"{prefix}{pattern.pattern} -> (namespace: {pattern.namespace})")
                self.print_urls(pattern.url_patterns, prefix + str(pattern.pattern))
