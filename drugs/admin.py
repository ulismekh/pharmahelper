
from django.contrib import admin
from .models import Drug, DrugDosage


class DrugDosageInline(admin.TabularInline):
    model = DrugDosage
    extra = 1


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'latin_name',
        'latin_genitive',
    )

    search_fields = (
        'name',
        'latin_name',
        'latin_genitive',
    )

    inlines = [DrugDosageInline]


@admin.register(DrugDosage)
class DrugDosageAdmin(admin.ModelAdmin):
    list_display = (
        'drug',
        'dosage_form',
        'prescription_status',
    )

    list_filter = (
        'dosage_form',
        'prescription_status',
    )

    search_fields = (
        'drug__name',
        'strength',
    )
