"""House-price-index service — refresh the 住宅價格指數 and suggest estate values.

Data source is **data.gov.tw open data REST** (chosen over scraping the 內政部
season XLSX to avoid file-parse errors). The index is repeat-sales /
transaction-based, so it tracks market value (not 公告現值). All network + CSV
parsing is isolated in :func:`_fetch_index_rows` so tests can monkeypatch it.

v1 uses a single configured region (default: the confirmed-working 臺北市全市
dataset). Point ``INDEX_DATASET_ID`` / ``INDEX_CATEGORY`` at the national (or the
property's county) dataset when available; per-estate region is a follow-up.
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.request

from sqlmodel import Session, select

from app.models.assets.estate import Estate, EstateJournal
from app.models.dashboard.house_price_index import (
    EstateValueSuggestion,
    HousePriceIndex,
    IndexRefreshResult,
)
from app.services.month_utils import month_end

# --- Source config (data.gov.tw). -----------------------------------------------
# region label → (dataset id, CSV 類別 row to keep or None = keep all). The 內政部
# 住宅價格指數 covers 全國 + the 6 直轄市 only (no full 22-county coverage). Only
# 臺北市 is pinned/confirmed (dataset 121969, column convention 期別/季指數/類別);
# the others need their data.gov.tw dataset ids. Unset regions are skipped on
# refresh and fall back to DEFAULT_REGION (全國) in suggestions.
DEFAULT_REGION = "全國"
INDEX_SOURCES: dict[str, tuple[str, str | None]] = {
    "臺北市": ("121969", "全市"),
    # TODO pin dataset ids (same 期別/季指數 columns expected):
    # "全國": ("<dataset_id>", None),
    # "新北市": ("<dataset_id>", None),
    # "桃園市": ("<dataset_id>", None),
    # "臺中市": ("<dataset_id>", None),
    # "臺南市": ("<dataset_id>", None),
    # "高雄市": ("<dataset_id>", None),
}
_DATASET_META_URL = "https://data.gov.tw/api/v2/rest/dataset/{id}"
_HTTP_TIMEOUT = 15


def _quarter_of_month(month: int) -> int:
    return (month - 1) // 3 + 1


def quarter_of_yyyymm(yyyymm: str) -> str | None:
    """YYYYMM → Gregorian quarter key 'YYYYQn'."""
    if len(yyyymm) < 6:
        return None
    return f"{yyyymm[:4]}Q{_quarter_of_month(int(yyyymm[4:6]))}"


def quarter_of_yyyymmdd(yyyymmdd: str) -> str | None:
    """YYYYMMDD → Gregorian quarter key 'YYYYQn'."""
    if not yyyymmdd or len(yyyymmdd) < 6:
        return None
    return f"{yyyymmdd[:4]}Q{_quarter_of_month(int(yyyymmdd[4:6]))}"


def roc_quarter_to_greg(period: str) -> str | None:
    """'101Q3' (ROC) → '2012Q3'. Already-Gregorian '2012Q3' passes through.

    Accepts ROC years (<1911 → +1911) or Gregorian years (>=1911 as-is).
    """
    m = re.match(r"\s*(\d{2,4})\s*[QqＱ]\s*([1-4])", period or "")
    if not m:
        return None
    year = int(m.group(1))
    if year < 1911:
        year += 1911
    return f"{year}Q{m.group(2)}"


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "networth/1.0"})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:  # noqa: S310
        return resp.read()


def _decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "big5", "cp950"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _resolve_csv_url(dataset_id: str) -> str | None:
    """data.gov.tw dataset metadata → first CSV resource download URL."""
    meta = json.loads(_decode(_http_get(_DATASET_META_URL.format(id=dataset_id))))
    result = meta.get("result", meta) if isinstance(meta, dict) else {}
    for dist in result.get("distribution", []) or []:
        fmt = (dist.get("resourceFormat") or "").upper()
        url = dist.get("resourceDownloadUrl")
        if "CSV" in fmt and url:
            return url
    return None


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def _fetch_index_rows(dataset_id: str, category: str | None) -> list[tuple[str, float]]:
    """Download + parse the index CSV → [(gregorian_quarter, index_value), ...].

    Tolerant to column naming: period column matched by '期別', index column by an
    exact '季指數' then any '指數' (excluding 變動率), category by '類別'. When the
    dataset has no category column the ``category`` filter is ignored (national
    single-series datasets). Network/parse errors propagate to the caller, which
    treats them as a best-effort no-op.
    """
    url = _resolve_csv_url(dataset_id)
    if not url:
        return []
    reader = csv.DictReader(io.StringIO(_decode(_http_get(url))))
    headers = [h.strip() for h in (reader.fieldnames or [])]
    if not headers:
        return []
    period_col = next((h for h in headers if "期別" in h), None)
    index_col = (
        next((h for h in headers if h.strip() == "季指數"), None)
        or next((h for h in headers if "指數" in h and "變動" not in h), None)
    )
    cat_col = next((h for h in headers if "類別" in h), None)
    if not period_col or not index_col:
        return []
    out: list[tuple[str, float]] = []
    for row in reader:
        # DictReader keys are the raw (unstripped) headers; map via stripped view.
        rec = {k.strip(): v for k, v in row.items() if k is not None}
        if cat_col and category and (rec.get(cat_col) or "").strip() != category:
            continue
        gq = roc_quarter_to_greg((rec.get(period_col) or "").strip())
        val = _to_float(rec.get(index_col))
        if gq and val is not None:
            out.append((gq, val))
    return out


def refresh_index(session: Session) -> IndexRefreshResult:
    """Best-effort refresh of every configured region; keep old data on failure.

    Loops :data:`INDEX_SOURCES`, fetching each region's series independently so one
    region failing doesn't lose the others. ``ok`` is True if any region refreshed.
    """
    total = 0
    refreshed: list[str] = []
    for region, (dataset_id, category) in INDEX_SOURCES.items():
        if not dataset_id:
            continue
        try:
            rows = _fetch_index_rows(dataset_id, category)
        except Exception:  # noqa: BLE001 — network/parse issues must not break the app
            rows = []
        if not rows:
            continue
        for quarter, value in rows:
            existing = session.get(HousePriceIndex, (region, quarter))
            if existing is not None:
                existing.index_value = value
            else:
                session.add(
                    HousePriceIndex(region=region, quarter=quarter, index_value=value)
                )
            total += 1
        refreshed.append(region)
    if total:
        session.commit()
    return IndexRefreshResult(
        region=", ".join(refreshed) or "—", upserted=total, ok=bool(refreshed)
    )


def _latest_index_at(
    session: Session, region: str, quarter: str | None
) -> HousePriceIndex | None:
    """Latest index row for ``region`` with ``quarter`` <= the given one (carry-forward)."""
    if not quarter:
        return None
    stmt = (
        select(HousePriceIndex)
        .where(HousePriceIndex.region == region)
        .where(HousePriceIndex.quarter <= quarter)
        .order_by(HousePriceIndex.quarter.desc())
    )
    return session.exec(stmt).first()


def _effective_region(session: Session, region: str | None) -> str:
    """The estate's region if it has any index data, else DEFAULT_REGION (全國)."""
    if region and session.exec(
        select(HousePriceIndex).where(HousePriceIndex.region == region)
    ).first():
        return region
    return DEFAULT_REGION


def suggest_estate_values(
    session: Session, vesting_month: str
) -> list[EstateValueSuggestion]:
    """Per-estate suggested market value = cost × (current index / obtain-quarter index).

    Uses each estate's ``region`` (falling back to 全國 when that region has no
    index data). ``suggested_market_value`` is null when either index point is
    missing (e.g. index not yet refreshed, or the obtain quarter predates the
    series) — the UI then just shows no suggestion.
    """
    current_q = quarter_of_yyyymm(vesting_month)
    estates = list(session.exec(select(Estate)).all())
    out: list[EstateValueSuggestion] = []
    for estate in estates:
        region = _effective_region(session, estate.region)
        current_row = _latest_index_at(session, region, current_q)
        cost = sum(
            j.excute_price
            for j in session.exec(
                select(EstateJournal)
                .where(EstateJournal.estate_id == estate.estate_id)
                .where(EstateJournal.excute_date <= month_end(vesting_month))
            ).all()
        )
        obtain_q = quarter_of_yyyymmdd(estate.obtain_date)
        base_row = _latest_index_at(session, region, obtain_q)
        suggested: float | None = None
        if (
            current_row is not None
            and base_row is not None
            and base_row.index_value
            and cost
        ):
            suggested = round(cost * current_row.index_value / base_row.index_value, 2)
        out.append(
            EstateValueSuggestion(
                estate_id=estate.estate_id,
                estate_name=estate.estate_name,
                cost=round(cost, 2),
                suggested_market_value=suggested,
                region=region,
                obtain_quarter=obtain_q,
                current_quarter=current_row.quarter if current_row is not None else None,
            )
        )
    return out
