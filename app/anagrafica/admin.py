from django.contrib import admin
from .models import Anagrafica


# Register your models here.
@admin.register(Anagrafica)
class AnagraficaAdmin(admin.ModelAdmin):
    list_display = [colonna.name for colonna in Anagrafica._meta.fields]
