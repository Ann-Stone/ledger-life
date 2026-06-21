"""Router tests for /utilities/import/* endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def _capture_tasks(monkeypatch) -> list[tuple]:
    captured: list[tuple] = []

    from fastapi import BackgroundTasks

    def _add(self, fn, *args, **kwargs):
        captured.append((fn.__name__, args, kwargs))

    monkeypatch.setattr(BackgroundTasks, "add_task", _add)
    return captured


def test_background_import_endpoints_return_202(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    for path, expected_msg in (
        ("/utilities/import/stock-prices", "stock import started"),
        ("/utilities/import/fx-rates", "fx import started"),
    ):
        resp = client.post(path, json={"period": "202601"})
        assert resp.status_code == 202, path
        body = resp.json()
        assert body["status"] == 1
        assert body["data"]["message"] == expected_msg
    assert len(captured) == 2
    assert {c[0] for c in captured} == {
        "import_stock_prices",
        "import_fx_rates",
    }


def test_invoice_import_accepts_upload_and_returns_result(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.models.utilities.imports import InvoiceImportResult
    from app.routers.utilities import imports as imports_module

    captured: dict[str, str] = {}

    def _fake_import(content: str) -> InvoiceImportResult:
        captured["content"] = content
        return InvoiceImportResult(imported=2, skipped=1, failed=0, errors=[])

    monkeypatch.setattr(imports_module, "import_invoices", _fake_import)

    csv_bytes = "M|Carrier|CAR1|20260105|S1|Coffee|INV-1|150|OK|\n".encode("utf-8")
    resp = client.post(
        "/utilities/import/invoices",
        files={"file": ("invoice.csv", csv_bytes, "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"] == {
        "imported": 2,
        "skipped": 1,
        "failed": 0,
        "months": [],
        "errors": [],
    }
    assert "INV-1" in captured["content"]


def test_invoice_import_requires_file(client: TestClient) -> None:
    resp = client.post("/utilities/import/invoices")
    assert resp.status_code == 422


def test_stock_import_schedules_background_task(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/stock-prices", json={"period": "202601"})
    assert resp.status_code == 202
    assert captured[0][0] == "import_stock_prices"
    assert captured[0][1] == ("202601",)


def test_period_validation_rejects_bad_format(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/stock-prices", json={"period": "2026-01"})
    assert resp.status_code == 422


def test_period_empty_is_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/fx-rates", json={"period": ""})
    assert resp.status_code == 202
    assert captured[0][1] == ("",)
