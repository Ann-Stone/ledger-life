"""Export OpenAPI spec as per-sub-router markdown + JSON files.

Used as the `export-docs` console script (see `pyproject.toml`). Output layout:

    api/docs/
    ├── api-reference.md                    (slim index — ~150 lines)
    ├── api-reference/
    │   ├── <domain>/<sub-router>.md        (one per sub-router; self-contained)
    │   └── <domain>.md                     (when domain has no sub-routers)
    └── openapi/
        ├── _shared.json                    (envelope + framework schemas)
        └── <domain>/<sub-router>.json      (paths + transitively-resolved schemas)

All committed and consumed by the frontend refactor; CI (`--check`) re-renders
into a temp dir and fails on any drift. Each output file is kept under 500
lines so the frontend granularization AI can pull just the slice it needs.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI


_DOMAIN_ORDER = [
    ("Settings", "/settings", "settings"),
    ("Monthly Report", "/monthly-report", "monthly-report"),
    ("Assets", "/assets", "assets"),
    ("Reports", "/reports", "reports"),
    ("Dashboard", "/dashboard", "dashboard"),
    ("Utilities", "/utilities", "utilities"),
    ("Health", "/health", "health"),
]


_MONTHLY_REPORT_INTRO = """### Polymorphic references

Journal rows carry two polymorphic foreign keys. Frontend forms must keep the
discriminator and the table consistent or the row will fail validation on the
server. The full matrix is:

| field group | type value | table value | id value points to | source endpoint |
| --- | --- | --- | --- | --- |
| `spend_way_*` | `account` | `Account` | `Account.id` (PK) | `GET /utilities/selections/accounts` |
| `spend_way_*` | `credit_card` | `Credit_Card` | `CreditCard.credit_card_id` | `GET /utilities/selections/credit-cards` |
| `action_main_*` | `Fixed` / `Floating` / `Income` / `Invest` / `Transfer` (user-configurable, mirrors `Code_Data.code_type`) | `Code_Data` | `Code_Data.code_id` (where `parent_id IS NULL`) | `GET /utilities/selections/codes` |
| `action_sub_*` | mirror of the sub-code's `Code_Data.code_type`, or `null` | `Code_Data` or `null` | `Code_Data.code_id` whose `parent_id == action_main`, or `null` | `GET /utilities/selections/codes/{action_main}` |

Hard rules the API enforces:

- `spend_way_table` must match the `spend_way_type` mapping above; mismatched values cause a 422.
- All three `action_sub_*` fields are populated together, or all three are `null`. Partial population is rejected.
- `action_main_table` is always `"Code_Data"` for journal entries created by the UI; legacy importers may emit other table names but new writes must use `Code_Data`.

"""


def load_app() -> FastAPI:
    """Import the live FastAPI app without starting uvicorn or touching the DB."""
    from app.main import app

    return app


def dump_openapi(app: FastAPI, out_path: Path) -> dict:
    """Write spec to `out_path` with deterministic ordering.

    Retained for tests and for callers that want the canonical full document
    (e.g. when validating against an external tool). Not written by the
    default `export-docs` run, which produces the per-sub-router split.
    """
    spec = app.openapi()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(spec, fp, indent=2, sort_keys=True, ensure_ascii=False)
        fp.write("\n")
    return spec


# ---------- Sub-router grouping ----------


def _domain_slug_for(path: str) -> tuple[str, str] | None:
    """Return (domain_label, domain_slug) for a path, or None if unknown."""
    for label, prefix, slug in _DOMAIN_ORDER:
        if path.startswith(prefix):
            return label, slug
    return None


def _subrouter_slug(path: str, domain_prefix: str) -> str:
    """Second path segment, e.g. `/settings/credit-cards/{id}` → 'credit-cards'."""
    rest = path[len(domain_prefix):].lstrip("/")
    if not rest:
        return "_root"
    first = rest.split("/", 1)[0]
    return first or "_root"


def _group_paths_by_subrouter(spec: dict) -> dict[tuple[str, str, str], list[tuple[str, str, dict]]]:
    """Return ``{(domain_label, domain_slug, subrouter_slug): [(METHOD, path, op), ...]}``.

    Applies sub-splits for sub-routers that would otherwise produce a single
    >500-line markdown file:

    - ``assets/<class>``: split into ``<class>`` (parent CRUD) and
      ``<class>-details`` (transaction-detail CRUD), matching the FE asset
      ticket layout (FE-028 vs FE-029, FE-030 vs FE-030-detail, etc.).
    - ``monthly-report/journals``: split into ``journals`` (entry CRUD +
      month query) and ``journals-analytics`` (the four chart endpoints).
    """
    groups: dict[tuple[str, str, str], list[tuple[str, str, dict]]] = {}
    paths = spec.get("paths", {}) or {}
    for path, methods in sorted(paths.items()):
        info = _domain_slug_for(path)
        if info is None:
            continue
        domain_label, domain_slug = info
        prefix = next(p for _, p, s in _DOMAIN_ORDER if s == domain_slug)
        sub = _subrouter_slug(path, prefix)
        sub = _refine_subrouter(domain_slug, sub, path)
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            groups.setdefault(
                (domain_label, domain_slug, sub), []
            ).append((method.upper(), path, operation))
    return groups


_ASSET_SUBROUTERS_WITH_DETAILS = {"stocks", "insurances", "estates", "loans"}
_JOURNAL_ANALYTICS_SUFFIXES = (
    "/expenditure-budget",
    "/expenditure-ratio",
    "/invest-ratio",
    "/liability",
)


def _refine_subrouter(domain_slug: str, sub: str, path: str) -> str:
    """Optionally rewrite ``sub`` to a finer slug to keep markdown files small."""
    if domain_slug == "assets" and sub in _ASSET_SUBROUTERS_WITH_DETAILS:
        if "/details" in path:
            return f"{sub}-details"
        if path.endswith("/selection"):
            return f"{sub}-selection"
    if domain_slug == "monthly-report" and sub == "journals":
        if path.endswith("-transaction"):
            return "journals-transactions"
        if any(path.endswith(suf) for suf in _JOURNAL_ANALYTICS_SUFFIXES):
            return "journals-analytics"
    if domain_slug == "settings" and sub == "codes":
        if path.endswith("/all-with-sub") or path.endswith("/sub-codes"):
            return "codes-tree"
    return sub


# ---------- Schema dependency resolution ----------


def _collect_refs(node, acc: set[str]) -> None:
    """Walk ``node`` and add every ``#/components/schemas/Name`` ref to ``acc``."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            acc.add(ref.split("/")[-1])
        for v in node.values():
            _collect_refs(v, acc)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, acc)


def _resolve_schema_closure(spec: dict, seed_paths: dict) -> set[str]:
    """Return the transitive set of schema names referenced from ``seed_paths``."""
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    found: set[str] = set()
    _collect_refs(seed_paths, found)
    queue = list(found)
    while queue:
        name = queue.pop()
        schema = schemas.get(name)
        if not schema:
            continue
        new: set[str] = set()
        _collect_refs(schema, new)
        for n in new - found:
            found.add(n)
            queue.append(n)
    return found


def _is_envelope_response(operation: dict) -> bool:
    """True if operation has a 200 (or 202) JSON response with a $ref schema."""
    responses = operation.get("responses", {}) or {}
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {}) or {}
        for media in content.values():
            schema = media.get("schema") or {}
            if "$ref" in schema:
                return True
            if (
                schema.get("type") == "array"
                and isinstance(schema.get("items"), dict)
                and ("$ref" in schema["items"] or schema["items"].get("type"))
            ):
                return True
            if schema.get("type") in {"object", "string", "integer", "number", "boolean"}:
                return True
    return False


def validate_discipline(spec: dict) -> list[str]:
    """Return a list of discipline violations; empty list = clean."""
    errors: list[str] = []

    paths = spec.get("paths", {}) or {}
    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            ident = f"{method.upper()} {path}"
            if not operation.get("summary"):
                errors.append(f"{ident}: missing summary")
            if not operation.get("description"):
                errors.append(f"{ident}: missing description")
            if not _is_envelope_response(operation):
                errors.append(f"{ident}: missing response_model")

    # FastAPI auto-injects HTTPValidationError/ValidationError for any route
    # with a request body or path/query params. They are framework-owned and
    # not subject to our discipline rules.
    framework_owned = {"HTTPValidationError", "ValidationError"}
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    for name, schema in sorted(schemas.items()):
        if name in framework_owned:
            continue
        for prop_name, prop in (schema.get("properties", {}) or {}).items():
            if "$ref" in prop:
                continue
            if not prop.get("description"):
                errors.append(f"schema {name}.{prop_name}: missing description")
    return errors


def _domain_for(path: str) -> str:
    for label, prefixes in _DOMAIN_ORDER:
        if any(path.startswith(p) for p in prefixes):
            return label
    return "Other"


def _resolve_ref(spec: dict, ref: str) -> dict:
    if not ref.startswith("#/components/schemas/"):
        return {}
    name = ref.split("/")[-1]
    return (spec.get("components", {}) or {}).get("schemas", {}).get(name, {}) or {}


def _params_table(parameters: list[dict]) -> str:
    if not parameters:
        return ""
    rows = ["| name | in | type | required | description |", "| --- | --- | --- | --- | --- |"]
    for p in parameters:
        schema = p.get("schema", {}) or {}
        type_ = schema.get("type", "")
        rows.append(
            f"| {p.get('name', '')} | {p.get('in', '')} | {type_} | "
            f"{'yes' if p.get('required') else 'no'} | "
            f"{p.get('description', '')} |"
        )
    return "\n".join(rows)


def _request_body_table(spec: dict, request_body: dict) -> str:
    if not request_body:
        return ""
    content = request_body.get("content", {}) or {}
    media = content.get("application/json")
    if not media:
        return ""
    schema = media.get("schema", {}) or {}
    return _props_table(spec, schema)


def _props_table(spec: dict, schema: dict) -> str:
    """Render a schema's properties as a Markdown table, resolving one $ref level."""
    if "$ref" in schema:
        schema = _resolve_ref(spec, schema["$ref"])
    props = schema.get("properties", {}) or {}
    if not props:
        return ""
    required = set(schema.get("required", []) or [])
    rows = ["| name | type | required | description |", "| --- | --- | --- | --- |"]
    for name, prop in props.items():
        if "$ref" in prop:
            type_ = prop["$ref"].split("/")[-1]
        elif prop.get("type") == "array":
            items = prop.get("items", {}) or {}
            if "$ref" in items:
                type_ = f"array<{items['$ref'].split('/')[-1]}>"
            else:
                type_ = f"array<{items.get('type', '')}>"
        else:
            type_ = prop.get("type", "")
            enum = prop.get("enum")
            if enum:
                type_ = f"{type_} (enum: {', '.join(repr(v) for v in enum)})"
        rows.append(
            f"| {name} | {type_} | {'yes' if name in required else 'no'} | "
            f"{prop.get('description', '')} |"
        )
    return "\n".join(rows)


def _data_inner_schema(spec: dict, envelope_schema: dict) -> tuple[dict | None, str]:
    """Return (resolved_data_schema, data_kind) where kind is 'object' | 'array' | ''."""
    props = envelope_schema.get("properties", {}) or {}
    data_prop = props.get("data") or {}
    # `data` may be a direct $ref, an array of $ref, or a union (anyOf) including null.
    candidates: list[dict] = []
    if "$ref" in data_prop:
        candidates.append(data_prop)
    if "anyOf" in data_prop:
        candidates.extend(data_prop["anyOf"])
    if data_prop.get("type") == "array":
        candidates.append(data_prop)
    if not candidates and data_prop:
        candidates.append(data_prop)

    for cand in candidates:
        if "$ref" in cand:
            return _resolve_ref(spec, cand["$ref"]), "object"
        if cand.get("type") == "array":
            items = cand.get("items", {}) or {}
            if "$ref" in items:
                return _resolve_ref(spec, items["$ref"]), "array"
            if items.get("type"):
                return items, "array"
    return None, ""


def _schema_example(spec: dict, schema: dict):
    """Resolve a schema's example, descending through $ref / arrays / anyOf."""
    if not schema:
        return None
    if "example" in schema:
        return schema["example"]
    if "$ref" in schema:
        return _schema_example(spec, _resolve_ref(spec, schema["$ref"]))
    if schema.get("type") == "array":
        items = schema.get("items", {}) or {}
        item_ex = _schema_example(spec, items)
        if item_ex is not None:
            return [item_ex]
    if "anyOf" in schema:
        for alt in schema["anyOf"]:
            ex = _schema_example(spec, alt)
            if ex is not None:
                return ex
    return None


def _composed_envelope_example(spec: dict, schema: dict):
    """Build a full envelope example (status/data/msg) by resolving the inner data example."""
    if "$ref" in schema:
        schema = _resolve_ref(spec, schema["$ref"])
    props = schema.get("properties", {}) or {}
    data_prop = props.get("data") or {}
    data_example = _schema_example(spec, data_prop)
    return {"status": 1, "data": data_example, "msg": "success"}


def _example_block(spec: dict, operation: dict) -> str:
    """Render the success-response example as a fenced JSON block, if present."""
    responses = operation.get("responses", {}) or {}
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {}) or {}
        media = content.get("application/json") or next(iter(content.values()), None)
        if not media:
            continue
        # 1. Endpoint-level example (highest precedence)
        example = media.get("example")
        if example is None:
            schema = media.get("schema", {}) or {}
            # 2. Compose envelope+data example by resolving inner schema's example
            example = _composed_envelope_example(spec, schema)
        if example is not None:
            return "```json\n" + json.dumps(example, indent=2, ensure_ascii=False) + "\n```"
    return ""


def _response_table(spec: dict, operation: dict) -> tuple[str, str, str]:
    """Return (envelope_table, data_table, data_kind). All may be empty strings."""
    responses = operation.get("responses", {}) or {}
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {}) or {}
        media = content.get("application/json") or next(iter(content.values()), None)
        if not media:
            continue
        schema = media.get("schema", {}) or {}
        if "$ref" in schema:
            schema = _resolve_ref(spec, schema["$ref"])
        envelope_md = _props_table(spec, schema)
        if not envelope_md:
            return "", "", ""
        data_schema, kind = _data_inner_schema(spec, schema)
        data_md = _props_table(spec, data_schema) if data_schema else ""
        return envelope_md, data_md, kind
    return "", "", ""


def _error_responses_block(spec: dict, operation: dict) -> str:
    """Render an Errors table (status / description / example) for 4xx/5xx responses."""
    responses = operation.get("responses", {}) or {}
    rows: list[str] = []
    for code, resp in sorted(responses.items()):
        if not isinstance(code, str) or not code.isdigit():
            continue
        if code.startswith("2"):
            continue
        description = (resp.get("description") or "").replace("\n", " ").strip()
        content = resp.get("content", {}) or {}
        media = content.get("application/json") or next(iter(content.values()), None)
        example_str = ""
        if media:
            example = media.get("example")
            if example is None:
                examples = media.get("examples") or {}
                if examples:
                    first = next(iter(examples.values()), {})
                    example = first.get("value") if isinstance(first, dict) else None
            if example is None:
                schema = media.get("schema", {}) or {}
                if "$ref" in schema:
                    schema = _resolve_ref(spec, schema["$ref"])
                example = schema.get("example")
            if example is not None:
                example_str = "`" + json.dumps(example, ensure_ascii=False).replace("|", "\\|") + "`"
        rows.append(f"| {code} | {description} | {example_str} |")
    if not rows:
        return ""
    header = ["| status | description | example |", "| --- | --- | --- |"]
    return "\n".join(header + rows)


def _render_operation(spec: dict, method: str, path: str, op: dict) -> list[str]:
    """Render a single endpoint block (heading + request + response + errors)."""
    lines: list[str] = [f"### {method} {path}", ""]
    if op.get("summary"):
        lines.extend([f"**{op['summary']}**", ""])
    if op.get("description"):
        lines.extend([op["description"], ""])
    params_md = _params_table(op.get("parameters", []) or [])
    body_md = _request_body_table(spec, op.get("requestBody", {}) or {})
    if params_md or body_md:
        lines.extend(["#### Request", ""])
        if params_md:
            lines.extend([params_md, ""])
        if body_md:
            lines.extend(["Body:", "", body_md, ""])
    envelope_md, data_md, data_kind = _response_table(spec, op)
    if envelope_md:
        lines.extend(["#### Response (200)", "", "Envelope:", "", envelope_md, ""])
        if data_md:
            label = "data (array item)" if data_kind == "array" else "data"
            lines.extend([f"{label}:", "", data_md, ""])
        example_md = _example_block(spec, op)
        if example_md:
            lines.extend(["Example:", "", example_md, ""])
    errors_md = _error_responses_block(spec, op)
    if errors_md:
        lines.extend(["#### Errors", "", errors_md, ""])
    return lines


def _slug_to_title(slug: str) -> str:
    """`'credit-cards'` → `'Credit Cards'`; `'monthly-report'` → `'Monthly Report'`."""
    return slug.replace("-", " ").replace("_", " ").title()


def _domain_intro(domain_label: str) -> str:
    """Return any domain-level intro markdown (e.g. polymorphism matrix)."""
    if domain_label == "Monthly Report":
        return _MONTHLY_REPORT_INTRO
    return ""


def render_subrouter_markdown(
    spec: dict,
    domain_label: str,
    domain_slug: str,
    subrouter_slug: str,
    operations: list[tuple[str, str, dict]],
) -> str:
    """Render a self-contained markdown file for a single sub-router."""
    title = (
        domain_label
        if subrouter_slug == "_root"
        else f"{domain_label} — {_slug_to_title(subrouter_slug)}"
    )
    lines = [f"# {title}", ""]
    lines.append(
        "Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. "
        "Do not edit by hand."
    )
    lines.append("")
    intro = _domain_intro(domain_label)
    if intro and subrouter_slug == "journals":
        # Polymorphism reference belongs alongside Journal CRUD.
        lines.append(intro.rstrip())
        lines.append("")
    lines.append("## Endpoints")
    lines.append("")
    for method, path, op in operations:
        lines.extend(_render_operation(spec, method, path, op))
    return "\n".join(lines).rstrip() + "\n"


def render_index_markdown(spec: dict, file_map: list[dict]) -> str:
    """Render the slim top-level api-reference.md index."""
    info = spec.get("info", {}) or {}
    lines = ["# Networth API Reference", ""]
    lines.append(
        "Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. "
        "Do not edit by hand."
    )
    lines.append("")
    lines.append(f"- OpenAPI version: `{spec.get('openapi', '')}`")
    if info.get("version"):
        lines.append(f"- API version: `{info['version']}`")
    lines.append("")

    lines.extend([
        "## How to read this directory",
        "",
        "Each sub-router has its own self-contained markdown file under "
        "`api-reference/<domain>/<sub-router>.md`, with the matching JSON slice "
        "at `openapi/<domain>/<sub-router>.json` for drill-down. Every file is "
        "kept under 500 lines so the frontend granularization AI can pull just "
        "the slice it needs without ingesting the whole API.",
        "",
        "Frontend tickets that touch a single resource (`/settings/accounts`, "
        "`/assets/stocks`, …) read **only** the matching sub-router file. "
        "Tickets that span a whole domain (e.g. `FE-003 — src/api/setting.ts`) "
        "read every file under that domain folder.",
        "",
    ])

    # Group entries by domain
    by_domain: dict[str, list[dict]] = {}
    for entry in file_map:
        by_domain.setdefault(entry["domain_label"], []).append(entry)

    lines.append("## Index")
    lines.append("")
    for label, _, _ in _DOMAIN_ORDER:
        entries = by_domain.get(label)
        if not entries:
            continue
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Sub-router | Markdown | OpenAPI slice | Endpoints |")
        lines.append("| --- | --- | --- | --- |")
        for entry in entries:
            sub = entry["subrouter_slug"]
            sub_label = "(root)" if sub == "_root" else sub
            ep_count = len(entry["operations"])
            lines.append(
                f"| `{sub_label}` | "
                f"[{entry['md_rel']}]({entry['md_rel']}) | "
                f"[{entry['json_rel']}]({entry['json_rel']}) | "
                f"{ep_count} |"
            )
        lines.append("")

    intro = _MONTHLY_REPORT_INTRO.rstrip()
    if intro:
        lines.append("## Monthly Report — Polymorphic references")
        lines.append("")
        lines.extend(intro.splitlines()[2:])  # drop the original "### Polymorphic references" heading line
        lines.append("")

    lines.extend([
        "## Shared OpenAPI components",
        "",
        "The `openapi/_shared.json` file contains schemas referenced by every "
        "sub-router (response envelope, error envelope, framework validation "
        "schemas). Each sub-router JSON inlines the schemas it uses, so it is "
        "self-contained — `_shared.json` is provided as a convenience for "
        "tools that want the canonical envelope definition without resolving "
        "duplicates.",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


# Schemas that live in `_shared.json` only. Per-sub-router JSON files
# reference them via $ref but do not duplicate the body.
_SHARED_SCHEMA_NAMES: frozenset[str] = frozenset({
    "ApiError",
    "HTTPValidationError",
    "ValidationError",
})


def build_subrouter_openapi(spec: dict, operations: list[tuple[str, str, dict]]) -> dict:
    """Build a paths-only OpenAPI slice for a sub-router.

    Schemas referenced by the paths are written as one file per schema under
    ``openapi/schemas/<Name>.json``; this slice lists the names it depends on
    in ``x-schema-files`` so AI consumers know which schema files to load
    alongside. Shared envelope/framework schemas (``ApiError`` etc.) are
    implicitly available in ``openapi/_shared.json`` and are not repeated in
    the per-router list.
    """
    paths_subset: dict = {}
    for method, path, op in operations:
        paths_subset.setdefault(path, {})[method.lower()] = op
    referenced = _resolve_schema_closure(spec, paths_subset)
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    schema_files = sorted(
        n for n in referenced if n in schemas and n not in _SHARED_SCHEMA_NAMES
    )
    # Paths are resolved from the openapi/ root, e.g. ``schemas/Foo.json``.
    return {
        "openapi": spec.get("openapi", ""),
        "info": dict(spec.get("info", {}) or {}),
        "paths": paths_subset,
        "x-schema-files": [f"schemas/{n}.json" for n in schema_files],
        "x-shared-file": "_shared.json",
    }


def build_per_schema_files(spec: dict) -> dict[str, dict]:
    """Return ``{schema_name: standalone_spec}`` — one OpenAPI doc per schema."""
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    out: dict[str, dict] = {}
    for name, body in schemas.items():
        if name in _SHARED_SCHEMA_NAMES:
            continue
        out[name] = {
            "openapi": spec.get("openapi", ""),
            "info": dict(spec.get("info", {}) or {}),
            "components": {"schemas": {name: body}},
        }
    return out


def build_shared_openapi(spec: dict) -> dict:
    """Build `_shared.json` containing only the cross-domain envelope schemas.

    Includes ``ApiError`` and FastAPI's framework validation schemas. The
    generic response envelope ``ApiResponse[T]`` is *not* a single schema in
    OpenAPI output — it expands per concrete ``T`` (e.g. ``ApiResponse_AccountRead_``)
    and lives next to its domain type, so we keep those alongside the domain
    schemas in each sub-router slice instead of bloating ``_shared.json`` with
    every instantiation.
    """
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    keep = {
        name: schemas[name]
        for name in sorted(schemas)
        if name in _SHARED_SCHEMA_NAMES
    }
    return {
        "openapi": spec.get("openapi", ""),
        "info": dict(spec.get("info", {}) or {}),
        "components": {"schemas": keep},
    }


def dump_markdown(markdown: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = markdown if markdown.endswith("\n") else markdown + "\n"
    out_path.write_text(text, encoding="utf-8", newline="\n")


def dump_json(payload: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, sort_keys=True, ensure_ascii=False)
        fp.write("\n")


def _output_dir() -> Path:
    """`api/docs/` resolved from this file's location."""
    return Path(__file__).resolve().parents[2] / "docs"


def _build_file_map(spec: dict) -> list[dict]:
    """Return the planned output layout (one entry per sub-router file)."""
    grouped = _group_paths_by_subrouter(spec)
    out: list[dict] = []
    for (domain_label, domain_slug, sub_slug), ops in grouped.items():
        if sub_slug == "_root":
            md_rel = f"api-reference/{domain_slug}.md"
            json_rel = f"openapi/{domain_slug}.json"
        else:
            md_rel = f"api-reference/{domain_slug}/{sub_slug}.md"
            json_rel = f"openapi/{domain_slug}/{sub_slug}.json"
        out.append({
            "domain_label": domain_label,
            "domain_slug": domain_slug,
            "subrouter_slug": sub_slug,
            "operations": ops,
            "md_rel": md_rel,
            "json_rel": json_rel,
        })

    # Sort: domains in canonical order, sub-routers alphabetically (with _root first)
    domain_order = {label: i for i, (label, _, _) in enumerate(_DOMAIN_ORDER)}
    out.sort(
        key=lambda e: (
            domain_order.get(e["domain_label"], 999),
            0 if e["subrouter_slug"] == "_root" else 1,
            e["subrouter_slug"],
        )
    )
    return out


def write_outputs(spec: dict, out_dir: Path) -> None:
    """Write the slim index, per-sub-router markdown + JSON, and `_shared.json`."""
    file_map = _build_file_map(spec)

    # Slim index
    dump_markdown(render_index_markdown(spec, file_map), out_dir / "api-reference.md")

    # Shared envelope/framework schemas
    dump_json(build_shared_openapi(spec), out_dir / "openapi" / "_shared.json")

    # Per-schema standalone files (one OpenAPI doc per Pydantic model).
    for name, sub_spec in build_per_schema_files(spec).items():
        dump_json(sub_spec, out_dir / "openapi" / "schemas" / f"{name}.json")

    # Per-sub-router markdown + paths-only json
    for entry in file_map:
        md = render_subrouter_markdown(
            spec,
            entry["domain_label"],
            entry["domain_slug"],
            entry["subrouter_slug"],
            entry["operations"],
        )
        dump_markdown(md, out_dir / entry["md_rel"])
        sub_spec = build_subrouter_openapi(spec, entry["operations"])
        dump_json(sub_spec, out_dir / entry["json_rel"])


def _snapshot_dir(path: Path) -> dict[str, bytes]:
    """Return a {relative_path: bytes} snapshot of every file under ``path``."""
    if not path.exists():
        return {}
    out: dict[str, bytes] = {}
    for fp in sorted(path.rglob("*")):
        if fp.is_file():
            out[fp.relative_to(path).as_posix()] = fp.read_bytes()
    return out


def _diff_snapshots(a: dict[str, bytes], b: dict[str, bytes]) -> list[str]:
    diffs: list[str] = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            if key not in a:
                diffs.append(f"+ {key}")
            elif key not in b:
                diffs.append(f"- {key}")
            else:
                diffs.append(f"~ {key}")
    return diffs


# Compatibility shim for the existing test suite, which imports
# ``render_markdown``. Returns the slim index.
def render_markdown(spec: dict) -> str:
    """Backwards-compatible wrapper returning the slim index markdown."""
    return render_index_markdown(spec, _build_file_map(spec))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export per-sub-router api-reference + openapi slices."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Re-export to a temp dir and fail on any diff vs committed files.",
    )
    args = parser.parse_args(argv)

    app = load_app()
    spec = app.openapi()
    errors = validate_discipline(spec)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    out_dir = _output_dir()

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            tmp_dir = Path(td)
            write_outputs(spec, tmp_dir)
            for sub in ("api-reference", "openapi"):
                tmp_snap = _snapshot_dir(tmp_dir / sub)
                live_snap = _snapshot_dir(out_dir / sub)
                if tmp_snap != live_snap:
                    print(f"{sub}/ drift:", file=sys.stderr)
                    for d in _diff_snapshots(live_snap, tmp_snap):
                        print(f"  {d}", file=sys.stderr)
                    return 1
            tmp_index = (tmp_dir / "api-reference.md").read_bytes()
            live_index_path = out_dir / "api-reference.md"
            if not live_index_path.exists() or live_index_path.read_bytes() != tmp_index:
                print("api-reference.md (index) drift", file=sys.stderr)
                return 1
        return 0

    # Wipe any previous split output to avoid stale files surviving a rename.
    for sub in ("api-reference", "openapi"):
        target = out_dir / sub
        if target.exists():
            shutil.rmtree(target)
    # Remove the legacy single-file artifact so the new layout is unambiguous.
    legacy_json = out_dir / "openapi.json"
    if legacy_json.exists():
        legacy_json.unlink()

    write_outputs(spec, out_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
