from django.shortcuts import render
from .models import Drug
from django.http import JsonResponse
from django.db.models import Q


def drug_list(request):
    drugs = Drug.objects.all()
    return render(request, 'drugs/drug_list.html', {
        'drugs': drugs
    })

def drug_search(request):
    query = request.GET.get("q", "").strip().casefold()

    if len(query) < 2:
        return JsonResponse([], safe=False)

    results = []

    for drug in Drug.objects.all():
        name = drug.name.casefold()
        latin_name = drug.latin_name.casefold()

        if query in name or query in latin_name:
            results.append({
                "id": drug.id,
                "name": drug.name,
                "latin_name": drug.latin_name,
                "form": drug.dosage_form,
            })

        if len(results) == 10:
            break

    return JsonResponse(results, safe=False)
