
from django import forms
from django.forms import formset_factory


class PrescriptionItemForm(forms.Form):

    drug = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    drug_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "drug-search",
            "placeholder": "Введите название препарата...",
            "autocomplete": "off"
        })
    )

    dosage_form = forms.ChoiceField(
        choices=[
            ("tablets", "Таблетки"),
            ("capsules", "Капсулы"),
            ("solution", "Раствор"),
            ("ointment", "Мазь"),
            ("powder", "Порошок"),
        ],
        label="Лекарственная форма"
    )

    dose = forms.CharField(
        max_length=100,
        label="Дозировка"
    )

    quantity = forms.IntegerField(
        min_value=1,
        label="Количество"
    )

    instructions = forms.CharField(
        widget=forms.Textarea,
        label="Способ применения"
    )


PrescriptionFormSet = formset_factory(
    PrescriptionItemForm,
    extra=1,
    max_num=20,
    validate_max=True,
    can_delete=True
)
