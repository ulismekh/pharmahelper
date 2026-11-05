from django.db import models

class Drug(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    latin_name = models.CharField(max_length=200, verbose_name="Название на латыни")
    latin_genitive = models.CharField(
        max_length=200,
        verbose_name="Родительный падеж"
    )

    dosage_form = models.CharField(
        max_length=100,
        verbose_name="Лекарственная форма"
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
