
import re
from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook


MNN_COLUMN = "МНН"
STATUS_COLUMN = "Условия отпуска"
FORM_COLUMN = "table.box_groups_name"

# Извлекаем лекарственную форму, не захватывая дозировку и упаковку.
FORM_PATTERNS = [
    r"таблетки",
    r"таблетки\s+покрытые\s+оболочкой",
    r"капсулы",
    r"капсулы\s+твердые",
    r"капсулы\s+мягкие",
    r"раствор\s+для\s+инъекций",
    r"раствор\s+для\s+инфузий",
    r"раствор\s+для\s+приема\s+внутрь",
    r"раствор\s+для\s+приёма\s+внутрь",
    r"раствор\s+для\s+подкожного\s+введения",
    r"раствор",
    r"суспензия",
    r"сироп",
    r"капли\s+глазные",
    r"капли\s+ушные",
    r"капли\s+назальные",
    r"капли",
    r"мазь",
    r"крем",
    r"гель",
    r"порошок\s+для\s+приготовления\s+раствора\s+для\s+инъекций",
    r"порошок\s+для\s+приготовления\s+раствора",
    r"порошок",
    r"лиофилизат",
    r"суппозитории",
    r"свечи",
    r"спрей\s+назальный",
    r"спрей",
    r"аэрозоль",
    r"эмульсия",
    r"концентрат\s+для\s+приготовления\s+раствора",
    r"концентрат",
    r"гранулы",
    r"пастилки",
    r"пластырь",
    r"драже",
    r"таблетки\s+для\s+рассасывания",
    r"аэрозоль\s+для\s+ингаляций",
    r"жидкость\s+для\s+ингаляций",
    r"пессарии",
    r"имплантат",
    r"шампунь",
    r"таблетка",
    r"инъекция",
    r"иньекция",
    r"[аa]эрозоль\s+для\s+ингаляций",
    r"микросферы",
    r"суспензии",
    r"инъекции",
    r"иньекции",
]

# Более длинные формы проверяются раньше коротких.
FORM_PATTERNS.sort(key=len, reverse=True)


def extract_forms(value):
    if not value:
        return []

    text = str(value).lower().replace("ё", "е")

    matches = []

    for pattern in FORM_PATTERNS:
        for match in re.finditer(
            rf"\b(?:{pattern})\b",
            text,
            flags=re.IGNORECASE
        ):
            matches.append({
                "start": match.start(),
                "end": match.end(),
                "form": match.group().strip().capitalize(),
            })

    # Сначала оставляем наиболее длинные совпадения
    matches.sort(
        key=lambda item: (-(item["end"] - item["start"]), item["start"])
    )

    selected = []

    for match in matches:
        overlaps = any(
            match["start"] >= item["start"]
            and match["end"] <= item["end"]
            for item in selected
        )

        if not overlaps:
            selected.append(match)

    # Возвращаем формы в порядке их появления в описании
    selected.sort(key=lambda item: item["start"])

    return list(dict.fromkeys(
        item["form"] for item in selected
    ))


def normalize_mnn(value):
    if not value:
        return ""

    return " ".join(str(value).strip().split())


def normalize_status(value):
    if not value:
        return ""

    text = str(value).strip().lower()

    if "неприменимо" in text:
        return "not_applicable"

    if "без рецепта" in text:
        return "otc"

    if "по рецепту" in text:
        return "prescription"

    return ""


class Command(BaseCommand):
    help = "Предварительный анализ государственного реестра лекарств"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Путь к Excel-файлу")

    def handle(self, *args, **options):
        file_path = options["file"]

        try:
            workbook = load_workbook(
                file_path,
                read_only=True,
                data_only=True
            )
        except Exception as error:
            raise CommandError(f"Не удалось открыть Excel: {error}")

        sheet = workbook.active

        headers = [
            str(cell).strip() if cell is not None else ""
            for cell in next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
        ]

        required = [MNN_COLUMN, STATUS_COLUMN, FORM_COLUMN]
        missing = [column for column in required if column not in headers]

        if missing:
            raise CommandError(
                "В Excel не найдены столбцы: " + ", ".join(missing)
            )

        indexes = {name: headers.index(name) for name in required}

        total = 0
        skipped_mnn = 0
        unique_mnn = set()
        dosage_pairs = set()
        unknown_forms = 0
        unknown_form_examples = []
        unknown_status = 0
        examples = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            total += 1

            mnn = normalize_mnn(row[indexes[MNN_COLUMN]])

            if not mnn or "отсутствует утвержденное мнн" in mnn.lower() or \
                    "отсутствует утверждённое мнн" in mnn.lower():
                skipped_mnn += 1
                continue

            unique_mnn.add(mnn.casefold())

            forms = extract_forms(row[indexes[FORM_COLUMN]])
            status = normalize_status(row[indexes[STATUS_COLUMN]])

            if not forms:
              unknown_forms += 1

              if len(unknown_form_examples) < 50:
                  unknown_form_examples.append({
                      "mnn": mnn,
                      "description": row[indexes[FORM_COLUMN]],
                  })

            if not status:
                unknown_status += 1

                self.stdout.write(
                    f"\nНЕИЗВЕСТНОЕ УСЛОВИЕ ОТПУСКА:"
                    f"\nМНН: {mnn}"
                    f"\nФорма: {row[indexes[FORM_COLUMN]]}"
                    f"\nЗначение: {row[indexes[STATUS_COLUMN]]}"
                )

            for form in forms:
                dosage_pairs.add((mnn.casefold(), form.casefold(), status))

            if len(examples) < 20:
                examples.append({
                    "mnn": mnn,
                    "forms": forms,
                    "status": status or "Не распознано",
                    "original": row[indexes[FORM_COLUMN]],
                })

        self.stdout.write("\n=== НЕРАСПОЗНАННЫЕ ФОРМЫ ===")

        for item in unknown_form_examples:
            self.stdout.write(
                f"\nМНН: {item['mnn']}\n"
                f"Описание: {item['description']}"
            )

        workbook.close()

        self.stdout.write("\n=== ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ ===")
        self.stdout.write(f"Всего строк: {total}")
        self.stdout.write(f"Строк без утверждённого МНН: {skipped_mnn}")
        self.stdout.write(f"Уникальных МНН: {len(unique_mnn)}")
        self.stdout.write(f"Предполагаемых вариантов формы: {len(dosage_pairs)}")
        self.stdout.write(f"Строк с нераспознанной формой: {unknown_forms}")
        self.stdout.write(f"Строк с нераспознанным условием отпуска: {unknown_status}")

        self.stdout.write("\n=== ПРИМЕРЫ РАСПОЗНАВАНИЯ ===")

        for item in examples:
            self.stdout.write(f"\nМНН: {item['mnn']}")
            self.stdout.write(f"Исходная ячейка: {item['original']}")
            self.stdout.write(f"Формы: {', '.join(item['forms']) or 'НЕ РАСПОЗНАНЫ'}")
            self.stdout.write(f"Условия отпуска: {item['status']}")

        self.stdout.write(
            self.style.SUCCESS(
                "\nАнализ завершён. База данных НЕ изменялась."
            )
        )
