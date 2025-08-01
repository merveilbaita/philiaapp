from django.contrib import admin

from salon.models import Personnel, Service, Prestation, Commission,Secteur

# Register your models here.
admin.site.register(Personnel)
admin.site.register(Service)
admin.site.register(Prestation)
admin.site.register(Commission)
admin.site.register(Secteur)