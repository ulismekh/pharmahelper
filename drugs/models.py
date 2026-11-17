
from django.db import models


class Drug(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Международное название"
    )

    latin_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Название на латыни"
    )

    latin_genitive = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Родительный падеж"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Препарат"
        verbose_name_plural = "Препараты"


class DrugDosage(models.Model):
    PRESCRIPTION_CHOICES = [
        ("prescription", "По рецепту"),
        ("otc", "Без рецепта"),
        ("not_applicable", "Неприменимо"),
    ]

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name="dosages",
        verbose_name="Препарат"
    )

    dosage_form = models.CharField(
        max_length=100,
        verbose_name="Лекарственная форма"
    )

    prescription_status = models.CharField(
        max_length=20,
        choices=PRESCRIPTION_CHOICES,
        blank=True,
        verbose_name="Условия отпуска"
    )

    def __str__(self):
        return f"{self.drug.name} — {self.dosage_form} {self.strength}"

    class Meta:
        verbose_name = "Дозировка препарата"
        verbose_name_plural = "Дозировки препаратов"
