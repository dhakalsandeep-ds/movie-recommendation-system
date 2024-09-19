from django.contrib import admin
from .models import Movie, Myrating, MyList
from django.contrib.auth.models import User, Group
from django.apps import apps
from django.utils.text import capfirst
admin.site.register(User)
admin.site.register(Group)

# Register your models here.
admin.site.register(Movie)
admin.site.register(Myrating)
admin.site.register(MyList)

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        if not self.has_permission(request):
         return redirect('%s?next=%s' % (self.login_url, request.path))

        models = apps.get_models()
        model_counts = {}  # Dictionary to hold model names and their counts
        
        for model in models:
            model_name = model._meta.verbose_name_plural.capitalize()
            count = model.objects.count()  # Get instance count
            model_counts[model_name] = count
        
        # Add model_counts to extra_context
        extra_context = extra_context or {}
        extra_context['model_counts'] = model_counts
        
        return super().index(request, extra_context=extra_context)
    def has_permission(self,request):
        return request.user.is_active and request.user.is_staff

# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')