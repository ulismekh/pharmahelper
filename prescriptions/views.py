
from django.shortcuts import render
from .forms import PrescriptionFormSet
from .recipe_generator import generate_recipe
from drugs.models import Drug


def generator(request):
    result = None

    if request.method == "POST":
        formset = PrescriptionFormSet(request.POST)

        if formset.is_valid():
            items = []
            missing_drug = False

            for index, data in enumerate(formset.cleaned_data):
                if not data or data.get("DELETE"):
                    continue

                drug = Drug.objects.filter(
                    id=data.get("drug")
                ).first()

                if not drug:
                    formset.forms[index].add_error(
                        "drug",
                        "Выберите препарат из подсказок."
                    )
                    missing_drug = True
                    continue

                items.append({
                    "drug": drug,
                    "dosage_form": data["dosage_form"],
                    "dose": data["dose"],
                    "quantity": data["quantity"],
                    "instructions": data["instructions"],
                })

            if items and not missing_drug:
                result = generate_recipe(items)

    else:
        formset = PrescriptionFormSet()

    return render(request, "prescriptions/generator.html", {
        "formset": formset,
        "result": result,
    })
