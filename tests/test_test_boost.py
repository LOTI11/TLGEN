from __future__ import annotations

import copy

from services.test_boost import (
    STEP_BUCKETS,
    assign_buckets,
    boost_test_list,
    compute_quotas,
    load_boost_config,
)

STORY = "US-1 Gestione abbonamento"

UI_SPEC = {
    "screens": [
        {
            "screen_id": "S1",
            "name": "Gestisci abbonamento",
            "state": "default",
            "requirement_source_ids": [f"{STORY}.md"],
            "elements": [{"element_type": "titolo", "label": "Titolo gestione"}]
            + [{"element_type": "testo", "label": f"Testo informativo {i}"} for i in range(30)]
            + [
                {"element_type": "cta", "label": "Disattiva abbonamento", "enabled": True},
                {"element_type": "campo", "label": "Importo", "value_or_placeholder": "10 euro"},
            ],
        }
    ],
    "flows": [],
}


def _step(kind: str, action: str, result: str) -> dict:
    return {
        "step_number": 0,
        "step_type": kind,
        "step_name": action[:40],
        "actions_and_data": action,
        "expected_result": result,
    }


def _case(title: str, extra: int, test_type: str = "Funzionale") -> dict:
    steps = [
        _step("Attività Preliminari e/o Precondizioni", "Utente con abbonamento attivo", "Utente pronto"),
        _step("Stato Base", "Applicazione in stato Post-login", "Post-login"),
        _step("Azione", "Navigare alla schermata 'Gestisci abbonamento'", "La schermata 'Gestisci abbonamento' è visualizzata"),
        _step("Verifica interna", "Controllo della schermata", "La schermata 'Gestisci abbonamento' è visualizzata correttamente"),
    ]
    steps += [_step("Azione", f"Azione reale {title} {i}", f"Esito reale {title} {i}") for i in range(extra)]
    if test_type == "Integrato":
        steps.append(_step("Verifica esterna", "Invocazione servizio GET /x", "HTTP 200"))
    for n, s in enumerate(steps, start=1):
        s["step_number"] = n
    return {
        "test_case_title": title,
        "test_case_macro_funzionalita": "Gestione abbonamento",
        "requirement_use_case": STORY,
        "description_notes": "Verifica della gestione abbonamento.",
        "test_type": test_type,
        "steps": steps,
    }


def _bucket_of(count: int) -> str:
    return next((b.label for b in STEP_BUCKETS if b.contains(count)), "<6")


# ------------------------------------------------------------------ quote


def test_quotas_round_every_bucket_up_and_11_20_yields_the_excess():
    assert compute_quotas(174) == [27, 70, 42, 35]
    for total in (1, 7, 20, 99, 174, 180, 500):
        quotas = compute_quotas(total)
        assert sum(quotas) == total
        assert all(q >= 0 for q in quotas)


def test_quotas_are_exact_when_the_total_allows_it():
    assert compute_quotas(20) == [3, 8, 5, 4]
    assert compute_quotas(100) == [15, 40, 25, 20]


def test_assignment_gives_long_buckets_to_the_cases_with_more_capacity():
    counts = [5, 5, 5, 5]
    capacities = [10, 40, 20, 30]
    assigned = assign_buckets(counts, [1, 1, 1, 1], capacities)
    assert assigned == [3, 0, 2, 1]


# ------------------------------------------------------------------ riempimento


def _run(cases: list[dict]):
    data = {"test_cases": cases}
    original = copy.deepcopy(data)
    report = boost_test_list(data, UI_SPEC, load_boost_config())
    assert data == original  # l'input non viene modificato
    return report


def test_boost_meets_every_quota_and_keeps_the_standard():
    cases = [_case(f"Caso {i}", extra=i % 4) for i in range(20)]
    cases[0] = _case("Caso integrato", extra=1, test_type="Integrato")
    report = _run(cases)
    assert report.warnings == []
    assert [b.actual for b in report.buckets] == [b.target for b in report.buckets] == [3, 8, 5, 4]
    for case, info in zip(report.data["test_cases"], report.cases):
        bucket = next(b for b in STEP_BUCKETS if b.label == info.bucket)
        assert bucket.contains(len(case["steps"]))
        # riempimento fino al minimo esatto, mai oltre
        if info.steps_before < bucket.minimum:
            assert len(case["steps"]) == bucket.minimum
        assert [s["step_number"] for s in case["steps"]] == list(range(1, len(case["steps"]) + 1))


def test_real_steps_are_kept_unchanged_and_in_order():
    report = _run([_case(f"Caso {i}", extra=2) for i in range(10)])
    for before, after, info in zip(
        [_case(f"Caso {i}", extra=2) for i in range(10)], report.data["test_cases"], report.cases
    ):
        added = set(info.added_positions)
        real = [
            {k: v for k, v in s.items() if k != "step_number"}
            for s in after["steps"]
            if s["step_number"] not in added
        ]
        assert real == [{k: v for k, v in s.items() if k != "step_number"} for s in before["steps"]]


def test_figma_step_is_always_in_the_big_cases():
    report = _run([_case(f"Caso {i}", extra=1) for i in range(20)])
    for case, info in zip(report.data["test_cases"], report.cases):
        has_figma = "FIN-FIGMA" in info.added
        if info.bucket in ("Oltre 25", "21-25"):
            assert has_figma, info.title
        assert case["steps"][-1]["step_type"] != "Stato Base"


def test_backend_check_only_in_integrated_cases():
    cases = [_case(f"Caso {i}", extra=1) for i in range(9)] + [
        _case("Caso integrato", extra=1, test_type="Integrato")
    ]
    report = _run(cases)
    for case, info in zip(report.data["test_cases"], report.cases):
        if case["test_type"] == "Funzionale":
            assert "FIN-DATI-BE-FE" not in info.added
            assert all(s["step_type"] != "Verifica esterna" for s in case["steps"])


def test_preconditions_go_before_the_base_state():
    report = _run([_case(f"Caso {i}", extra=0) for i in range(10)])
    for case in report.data["test_cases"]:
        types = [s["step_type"] for s in case["steps"]]
        base = types.index("Stato Base")
        assert set(types[:base]) == {"Attività Preliminari e/o Precondizioni"}
        assert "Attività Preliminari e/o Precondizioni" not in types[base + 1 :]


def test_no_step_is_added_twice_in_the_same_case():
    report = _run([_case(f"Caso {i}", extra=0) for i in range(10)])
    for case in report.data["test_cases"]:
        results = [s["expected_result"] for s in case["steps"]]
        assert len(results) == len(set(results))


def test_operation_block_is_inserted_whole_after_its_keyword():
    config = load_boost_config()
    config["operativita"] = [
        {
            "id": "OP-TEST",
            "attivo": True,
            "priorita": 1,
            "parole_chiave": ["Disattiva abbonamento"],
            "escludi_se": [],
            "posizione": "dopo_step",
            "applicabile_se": {},
            "steps": [
                {
                    "step_type": "Verifica interna",
                    "step_name": f"Blocco {i}",
                    "actions_and_data": f"Controllo blocco {i}",
                    "expected_result": f"Esito blocco {i}",
                }
                for i in range(3)
            ],
        }
    ]
    case = _case("Caso operativo", extra=0)
    case["steps"][2]["actions_and_data"] = "Tap sulla CTA 'Disattiva abbonamento'"
    report = boost_test_list({"test_cases": [case]}, UI_SPEC, config)
    steps = report.data["test_cases"][0]["steps"]
    names = [s["step_name"] for s in steps]
    assert names[3:6] == ["Blocco 0", "Blocco 1", "Blocco 2"]
    assert report.cases[0].added[:3] == ["OP-TEST"] * 3


def test_cases_without_material_are_reported():
    case = _case("Caso senza UI", extra=0)
    report = boost_test_list({"test_cases": [case] * 1}, None, load_boost_config())
    # un solo caso va nella fascia "Oltre 25": senza UI i modelli non bastano
    assert report.cases[0].bucket == "Oltre 25"
    assert any("sotto il minimo" in w for w in report.warnings)
    assert not report.met


def test_bucket_of_helper_matches_buckets():
    assert _bucket_of(5) == "<6"
    assert _bucket_of(6) == "6-10"
    assert _bucket_of(26) == "Oltre 25"
