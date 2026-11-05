from django.contrib import admin
from .models import Drug

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'latin_name',
        'latin_genitive',
        'dosage_form',
    )

    search_fields = (
        'name',
        'latin_name',
        'latin_genitive',
    )

    list_filter = ('dosage_form',)
