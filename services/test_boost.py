"""Modalità Test Boost: distribuzione obbligatoria del numero di step.

Vincolo sull'intera test list: 15% dei casi oltre 25 step, 40% tra 21 e 25,
25% tra 11 e 20, 20% tra 6 e 10 (precondizioni e Stato Base inclusi).

Il modello genera i casi come sempre; il Boost lavora dopo, sul JSON finale:

1. quote per fascia sul numero totale di casi (per eccesso sulle fasce lunghe,
   il resto alla fascia 6-10);
2. fasce assegnate in base agli step reali: i casi più lunghi vanno nelle fasce
   più lunghe, così il riempimento è il minimo possibile;
3. ogni caso sotto il minimo della propria fascia viene completato con gli step di
   ``parser/boost/boostSteps.json`` fino al minimo esatto: prima i blocchi di
   operatività attivati dalle parole chiave, poi i modelli in ordine di priorità
   (verifiche degli elementi delle schermate raggiunte, layout, chiusura,
   precondizioni);
4. ogni caso modificato viene ricontrollato con ``check_standards``.

Gli step reali non vengono mai tolti né modificati; gli step aggiunti sono
registrati nel report (non nel file esportato).
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models.TestCase import StepType
from models.llm_schemas import CaseKind, DetailCase, DetailStep
from services.json_generation import TEST_CASES_JSON_FILE, save_json
from services.test_case_generation import check_standards, ui_for_story

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOST_STEPS_FILE = PROJECT_ROOT / "parser" / "boost" / "boostSteps.json"
# La test list completata sostituisce TEST_CASES_JSON_FILE (letto dall'export);
# quella generata dal modello resta in PRE_BOOST_FILE, gli step aggiunti in BOOST_REPORT_FILE.
PRE_BOOST_FILE = TEST_CASES_JSON_FILE.with_name("test_cases_pre_boost.json")
BOOST_REPORT_FILE = TEST_CASES_JSON_FILE.with_name("boost_report.json")


@dataclass(frozen=True)
class StepBucket:
    label: str
    minimum: int
    maximum: int | None  # None = nessun massimo
    share: float

    def contains(self, count: int) -> bool:
        return count >= self.minimum and (self.maximum is None or count <= self.maximum)


# Dalla più lunga alla più corta: l'ordine conta per l'assegnazione.
STEP_BUCKETS: tuple[StepBucket, ...] = (
    StepBucket("Oltre 25", 26, None, 0.15),
    StepBucket("21-25", 21, 25, 0.40),
    StepBucket("11-20", 11, 20, 0.25),
    StepBucket("6-10", 6, 10, 0.20),
)

_UNLIMITED = 10**6  # obiettivo usato per misurare la capacità di un caso
_QUOTED = re.compile(r"'([^']+)'")
_PLACEHOLDER = re.compile(r"\{(\w+)\}")
_STEP_TEXT_FIELDS = ("step_name", "actions_and_data", "expected_result")


# ------------------------------------------------------------------ report


@dataclass
class BucketResult:
    bucket: StepBucket
    target: int
    actual: int = 0

    @property
    def met(self) -> bool:
        return self.actual >= self.target


@dataclass
class CaseBoost:
    index: int
    title: str
    bucket: str
    steps_before: int
    steps_after: int
    added: list[str] = field(default_factory=list)  # id dei modelli/blocchi usati
    added_positions: list[int] = field(default_factory=list)  # numeri degli step aggiunti


@dataclass
class BoostReport:
    data: dict[str, Any]
    buckets: list[BucketResult]
    cases: list[CaseBoost]
    warnings: list[str]

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    @property
    def real_steps(self) -> int:
        return sum(c.steps_before for c in self.cases)

    @property
    def added_steps(self) -> int:
        return sum(c.steps_after - c.steps_before for c in self.cases)

    @property
    def met(self) -> bool:
        return all(b.met for b in self.buckets) and not self.warnings

    def to_json(self) -> dict[str, Any]:
        return {
            "buckets": [
                {
                    "fascia": b.bucket.label,
                    "obiettivo": b.target,
                    "ottenuto": b.actual,
                    "percentuale": round(100 * b.actual / self.total_cases, 1)
                    if self.total_cases
                    else 0,
                }
                for b in self.buckets
            ],
            "step_reali": self.real_steps,
            "step_aggiunti": self.added_steps,
            "avvisi": self.warnings,
            "casi": [
                {
                    "test_case_title": c.title,
                    "fascia": c.bucket,
                    "step_prima": c.steps_before,
                    "step_dopo": c.steps_after,
                    "step_aggiunti": c.added_positions,
                    "modelli": c.added,
                }
                for c in self.cases
                if c.added
            ],
        }


# ------------------------------------------------------------------ quote e fasce


# Fascia che cede i casi in eccesso quando tutte le quote sono arrotondate per eccesso
# (scelta dell'utente del 25/11: le altre tre restano sempre per eccesso).
YIELDING_BUCKET = "11-20"


def compute_quotas(
    total: int, buckets: Sequence[StepBucket] = STEP_BUCKETS, yielding: str = YIELDING_BUCKET
) -> list[int]:
    """Casi per fascia: ogni quota per eccesso; l'eccedenza la cede ``yielding``.

    Le percentuali sommano a 100, quindi con la maggior parte dei totali gli
    arrotondamenti per eccesso superano i casi disponibili (174 casi: 27+70+44+35 =
    176): i casi in più vengono tolti dalla fascia ``yielding`` e, se non basta,
    dalle altre partendo dalla più corta.
    """
    quotas = [math.ceil(round(total * b.share, 6)) for b in buckets]
    excess = sum(quotas) - total
    labels = [b.label for b in buckets]
    order = ([labels.index(yielding)] if yielding in labels else []) + list(range(len(buckets) - 1, -1, -1))
    for i in order:
        if excess <= 0:
            break
        cut = min(excess, quotas[i])
        quotas[i] -= cut
        excess -= cut
    return quotas


def assign_buckets(
    step_counts: Sequence[int], quotas: Sequence[int], capacities: Sequence[int] | None = None
) -> list[int]:
    """Indice di fascia per ogni caso: alle fasce più lunghe i casi che possono arrivarci.

    ``capacities`` = step massimi raggiungibili da ogni caso (reali + riempitivi
    applicabili). Ordine: prima la capacità, poi gli step reali (a parità di
    capacità serve meno riempimento).
    """
    capacities = step_counts if capacities is None else capacities
    order = sorted(range(len(step_counts)), key=lambda i: (-capacities[i], -step_counts[i], i))
    assigned = [len(quotas) - 1] * len(step_counts)
    position = 0
    for bucket_index, quota in enumerate(quotas):
        for i in order[position : position + quota]:
            assigned[i] = bucket_index
        position += quota
    return assigned


# ------------------------------------------------------------------ configurazione


def load_boost_config(path: Path = BOOST_STEPS_FILE) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            config = json.load(handle)
    except OSError as exc:
        raise ValueError(f"File degli step del Test Boost non leggibile ({path}): {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path.name} non è un JSON valido (riga {exc.lineno}, colonna {exc.colno}): {exc.msg}"
        ) from exc
    config.setdefault("steps", [])
    config.setdefault("operativita", [])
    config.setdefault("limiti_per_caso", {})
    return config


# ------------------------------------------------------------------ riempimento


def _fold(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().casefold()


def _step_text(step: Mapping[str, Any]) -> str:
    return " ".join(str(step.get(name) or "") for name in _STEP_TEXT_FIELDS)


def _render(template: str, values: Mapping[str, Any]) -> str | None:
    """Sostituisce i segnaposto; None se uno resta senza valore."""
    missing = False

    def replace(match: re.Match[str]) -> str:
        nonlocal missing
        value = values.get(match.group(1))
        if value in (None, ""):
            missing = True
            return ""
        return str(value).strip()

    text = _PLACEHOLDER.sub(replace, template)
    return None if missing else text


@dataclass
class _Insert:
    key: tuple[int, int]  # (indice dello step reale di riferimento, -1 prima / +1 dopo)
    step: dict[str, Any]
    source: str


class _CaseFiller:
    """Completa un singolo caso fino a ``target`` step."""

    def __init__(
        self,
        case: Mapping[str, Any],
        config: Mapping[str, Any],
        ui_spec: Mapping[str, Any] | None,
        target: int,
        maximum: int | None,
        bucket: str | None = None,
    ) -> None:
        self.case = case
        self.bucket = bucket
        self.config = config
        self.steps: list[dict[str, Any]] = [dict(s) for s in case.get("steps") or []]
        self.target = target
        self.maximum = maximum
        self.inserts: list[_Insert] = []
        self.category_count: dict[str, int] = {}
        self.texts = [_fold(_step_text(s)) for s in self.steps]
        self.all_text = " ".join(self.texts)
        self.check_text = " ".join(
            t
            for s, t in zip(self.steps, self.texts)
            if s.get("step_type") in (StepType.VERIFICA_INTERNA.value, StepType.VERIFICA_ESTERNA.value)
        )
        self.seen_results = {_fold(s.get("expected_result")) for s in self.steps}
        types = [s.get("step_type") for s in self.steps]
        self.base = (
            types.index(StepType.STATO_BASE.value) if StepType.STATO_BASE.value in types else 0
        )
        base_text = self.texts[self.base] if self.steps else ""
        self.context = {
            "test_type": case.get("test_type"),
            "stato_base": "Pre-login" if "pre-login" in base_text else "Post-login",
            "ui": bool(ui_spec),
            "funzionalita": bool(str(case.get("test_case_macro_funzionalita") or "").strip()),
        }
        story_ui = ui_for_story(ui_spec, str(case.get("requirement_use_case") or "")) if ui_spec else None
        self.screens = self._reached_screens((story_ui or {}).get("screens") or [])

    # -------------------------------------------------------------- schermate

    def _reached_screens(self, screens: Sequence[Mapping[str, Any]]) -> list[tuple[int, Mapping[str, Any]]]:
        """Schermate citate negli step (tra apici), con lo step dopo cui inserire le verifiche."""
        quoted = [{_fold(q) for q in _QUOTED.findall(_step_text(s))} for s in self.steps]
        by_name: dict[str, list[Mapping[str, Any]]] = {}
        for screen in screens:
            by_name.setdefault(_fold(screen.get("name")), []).append(screen)
        reached: list[tuple[int, Mapping[str, Any]]] = []
        for name, variants in by_name.items():
            if not name:
                continue
            mentions = [i for i, q in enumerate(quoted) if name in q and i > self.base]
            if not mentions:
                continue
            checks = [
                i for i in mentions if self.steps[i].get("step_type") == StepType.VERIFICA_INTERNA.value
            ]
            anchor = (checks or mentions)[0]
            states = [v for v in variants if _fold(v.get("state")) and _fold(v.get("state")) in self.all_text]
            default = [v for v in variants if _fold(v.get("state")) in ("", "default")]
            reached.append((anchor, (states or default or variants)[0]))
        reached.sort(key=lambda item: item[0])
        return reached

    # -------------------------------------------------------------- condizioni

    def _case_condition(self, conditions: Mapping[str, Any]) -> bool:
        for key in ("test_type", "stato_base"):
            if key in conditions and _fold(conditions[key]) != _fold(self.context[key]):
                return False
        for key in ("ui", "funzionalita"):
            if key in conditions and bool(conditions[key]) != self.context[key]:
                return False
        return True

    @staticmethod
    def _element_condition(
        conditions: Mapping[str, Any], element: Mapping[str, Any], specific_types: set[str]
    ) -> bool:
        kind = _fold(element.get("element_type"))
        wanted = conditions.get("element_type")
        if wanted is not None:
            if wanted == "*":
                if kind in specific_types:
                    return False
            elif _fold(wanted) != kind:
                return False
        if "enabled" in conditions and (element.get("enabled") is not False) != bool(conditions["enabled"]):
            return False
        if "required" in conditions and (element.get("required") is True) != bool(conditions["required"]):
            return False
        if "valore" in conditions and bool(str(element.get("value_or_placeholder") or "").strip()) != bool(
            conditions["valore"]
        ):
            return False
        return True

    # -------------------------------------------------------------- inserimento

    @property
    def count(self) -> int:
        return len(self.steps) + len(self.inserts)

    def _room(self, size: int = 1) -> bool:
        return self.count + size <= self.target

    def _limit_ok(self, category: str) -> bool:
        limit = (self.config.get("limiti_per_caso") or {}).get(category)
        return limit is None or self.category_count.get(category, 0) < limit

    def _make_step(self, template: Mapping[str, Any], values: Mapping[str, Any]) -> dict[str, Any] | None:
        step = {"step_number": 0, "step_type": template.get("step_type")}
        for name in _STEP_TEXT_FIELDS:
            text = _render(str(template.get(name) or ""), values)
            if not text:
                return None
            step[name] = text
        result = _fold(step["expected_result"])
        if result in self.seen_results:
            return None
        return step

    def _add(self, key: tuple[int, int], step: dict[str, Any], source: str, category: str) -> None:
        self.inserts.append(_Insert(key, step, source))
        self.seen_results.add(_fold(step["expected_result"]))
        self.category_count[category] = self.category_count.get(category, 0) + 1

    def _position(self, where: str, anchor: int | None = None) -> tuple[int, int] | None:
        if where == "inizio":
            return (self.base, -1)
        if where == "fine":
            return (len(self.steps), -1)
        if anchor is None:
            return None
        if where == "prima_step":
            return (anchor, -1) if anchor > self.base else None
        return (anchor, 1)  # dopo_step / dopo_schermata

    def _fill_operations(self) -> None:
        blocks = [b for b in self.config.get("operativita") or [] if b.get("attivo")]
        for block in sorted(blocks, key=lambda b: b.get("priorita", 99)):
            if self.count >= self.target:
                return
            if not self._case_condition(block.get("applicabile_se") or {}):
                continue
            if any(_fold(word) in self.all_text for word in block.get("escludi_se") or []):
                continue
            words = [_fold(w) for w in block.get("parole_chiave") or [] if _fold(w)]
            anchor = next(
                (i for i, t in enumerate(self.texts) if i > self.base and any(w in t for w in words)),
                None,
            )
            key = self._position(block.get("posizione", "dopo_step"), anchor)
            if key is None:
                continue
            steps = [s for s in (self._make_step(t, {}) for t in block.get("steps") or []) if s]
            if not steps or not self._room(len(steps)):
                continue  # un blocco entra intero o non entra
            for step in steps:
                self._add(key, step, block.get("id", "operativita"), "operativita")

    def _candidates(self) -> list[tuple[int, int, tuple[int, int], dict[str, Any], str, str]]:
        """(priorità, ordine, posizione, step, id, categoria) per tutti i modelli applicabili."""
        templates = self.config.get("steps") or []
        specific = {
            _fold((t.get("applicabile_se") or {}).get("element_type"))
            for t in templates
            if (t.get("applicabile_se") or {}).get("element_type") not in (None, "*")
        }
        values_case = {"funzionalita": self.case.get("test_case_macro_funzionalita")}
        found: list[tuple[int, int, tuple[int, int], dict[str, Any], str, str]] = []
        order = 0
        for template in templates:
            conditions = template.get("applicabile_se") or {}
            if not self._case_condition(conditions):
                continue
            repeat = template.get("ripeti_per")
            priority = int(template.get("priorita", 99))
            if repeat in ("elemento", "schermata"):
                for anchor, screen in self.screens:
                    key = self._position(template.get("posizione", "dopo_schermata"), anchor)
                    if key is None:
                        continue
                    base_values = {**values_case, "schermata": screen.get("name")}
                    items = (screen.get("elements") or []) if repeat == "elemento" else [None]
                    for element in items:
                        values = dict(base_values)
                        if element is not None:
                            if not self._element_condition(conditions, element, specific):
                                continue
                            label = str(element.get("label") or "").strip()
                            if not label or _fold(label) in self.check_text:
                                continue  # già verificato dal caso
                            values.update(elemento=label, valore=element.get("value_or_placeholder"))
                        order += 1
                        found.append((priority, order, key, dict(template), template.get("id", ""), json.dumps(values)))
            else:
                key = self._position(template.get("posizione", "fine"))
                if key is None:
                    continue
                order += 1
                found.append((priority, order, key, dict(template), template.get("id", ""), json.dumps(values_case)))
        found.sort(key=lambda item: (item[0], item[1]))
        return found

    def _fill_mandatory(self) -> None:
        """Modelli con ``obbligatorio_fasce``: entrano per primi nei casi di quelle fasce."""
        values = {"funzionalita": self.case.get("test_case_macro_funzionalita")}
        for template in self.config.get("steps") or []:
            if self.count >= self.target:
                return
            if self.bucket not in (template.get("obbligatorio_fasce") or []):
                continue
            if template.get("ripeti_per") or not self._case_condition(template.get("applicabile_se") or {}):
                continue
            key = self._position(template.get("posizione", "fine"))
            step = self._make_step(template, values) if key else None
            if step:
                self._add(key, step, template.get("id", ""), template.get("categoria", ""))

    def fill(self) -> list[dict[str, Any]]:
        if self.count < self.target:
            self._fill_mandatory()
        if self.count < self.target:
            self._fill_operations()
        if self.count < self.target:
            for _, _, key, template, source, values in self._candidates():
                if self.count >= self.target:
                    break
                category = template.get("categoria", "")
                if not self._limit_ok(category):
                    continue
                step = self._make_step(template, json.loads(values))
                if step:
                    self._add(key, step, source, category)
        return self._merge()

    def _merge(self) -> list[dict[str, Any]]:
        rows: list[tuple[tuple[int, int, int], dict[str, Any], str | None]] = [
            ((i, 0, 0), step, None) for i, step in enumerate(self.steps)
        ]
        rows += [((ins.key[0], ins.key[1], n), ins.step, ins.source) for n, ins in enumerate(self.inserts)]
        rows.sort(key=lambda row: row[0])
        merged: list[dict[str, Any]] = []
        self.added_positions: list[int] = []
        self.added_sources: list[str] = []
        for number, (_, step, source) in enumerate(rows, start=1):
            merged.append({**step, "step_number": number})
            if source is not None:
                self.added_positions.append(number)
                self.added_sources.append(source)
        return merged


# ------------------------------------------------------------------ entry point


def _standard_issues(case: Mapping[str, Any]) -> list[str]:
    try:
        detail = DetailCase(
            case_ref="",
            description_notes=str(case.get("description_notes") or ""),
            steps=[DetailStep(**s) for s in case.get("steps") or []],
        )
        return check_standards(detail, CaseKind(case.get("test_type")))
    except (ValueError, TypeError) as exc:
        return [f"caso non valido: {exc}"]


def boost_test_list(
    data: Mapping[str, Any],
    ui_spec: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
    buckets: Sequence[StepBucket] = STEP_BUCKETS,
) -> BoostReport:
    """Applica il Boost alla test list (``{"test_cases": [...]}``) e restituisce il report."""
    config = load_boost_config() if config is None else config
    cases = list(data.get("test_cases") or [])
    counts = [len(c.get("steps") or []) for c in cases]
    quotas = compute_quotas(len(cases), buckets)
    capacities = [
        len(_CaseFiller(c, config, ui_spec, _UNLIMITED, None).fill()) for c in cases
    ]
    assigned = assign_buckets(counts, quotas, capacities)
    warnings: list[str] = []
    boosted: list[dict[str, Any]] = []
    results: list[CaseBoost] = []

    for index, (case, bucket_index) in enumerate(zip(cases, assigned)):
        bucket = buckets[bucket_index]
        title = str(case.get("test_case_title") or f"caso {index + 1}")
        info = CaseBoost(index, title, bucket.label, counts[index], counts[index])
        new_case = dict(case)
        if counts[index] < bucket.minimum:
            filler = _CaseFiller(case, config, ui_spec, bucket.minimum, bucket.maximum, bucket.label)
            steps = filler.fill()
            candidate = {**case, "steps": steps}
            issues = _standard_issues(candidate)
            if issues:
                warnings.append(f"'{title}': step aggiunti scartati, non conformi allo standard ({issues[0]})")
            else:
                new_case = candidate
                info.steps_after = len(steps)
                info.added = filler.added_sources
                info.added_positions = filler.added_positions
            if info.steps_after < bucket.minimum:
                warnings.append(
                    f"'{title}': {info.steps_after} step, sotto il minimo di {bucket.minimum} "
                    f"della fascia {bucket.label} (modelli insufficienti)"
                )
        elif bucket.maximum is not None and counts[index] > bucket.maximum:
            warnings.append(
                f"'{title}': {counts[index]} step reali, oltre il massimo della fascia {bucket.label}"
            )
        boosted.append(new_case)
        results.append(info)

    bucket_results = [BucketResult(b, q) for b, q in zip(buckets, quotas)]
    for info in results:
        for result in bucket_results:
            if result.bucket.contains(info.steps_after):
                result.actual += 1
                break
    return BoostReport({**data, "test_cases": boosted}, bucket_results, results, warnings)


def run_boost(
    data: Mapping[str, Any],
    ui_spec: Mapping[str, Any] | None = None,
    *,
    json_file: Path = TEST_CASES_JSON_FILE,
    pre_boost_file: Path = PRE_BOOST_FILE,
    report_file: Path = BOOST_REPORT_FILE,
    config: Mapping[str, Any] | None = None,
) -> tuple[BoostReport, str]:
    """Boost con salvataggio: originale, test list completata (per l'export) e report.

    Restituisce il report e il testo del JSON completato.
    """
    save_json(data, pre_boost_file)
    report = boost_test_list(data, ui_spec, config)
    text = save_json(report.data, json_file)
    save_json(report.to_json(), report_file)
    return report, text


def bucket_summary(report: BoostReport) -> str:
    """Riga breve per lo stato dello stage: ottenuto/obiettivo per fascia."""
    return " · ".join(f"{b.bucket.label}: {b.actual}/{b.target}" for b in report.buckets)
