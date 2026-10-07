from __future__ import annotations

import copy
from typing import Any

import pytest

from codegen.build import assign_names, clean_text
from codegen.diff import summarize
from codegen.naming import field_name, pascal, snake, upper_snake
from codegen.spec import Spec, method_path


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("organizationId", "organization_id"),
        ("init_by_posOrder", "init_by_pos_order"),
        ("ErrorCode", "error_code"),
        ("sumWithoutVAT", "sum_without_vat"),
        ("cash-flow-category", "cash_flow_category"),
        ("RGBColor", "rgb_color"),
    ],
)
def test_snake(name: str, expected: str) -> None:
    assert snake(name) == expected


def test_other_names() -> None:
    assert pascal("internal_finance_accounts") == "InternalFinanceAccounts"
    assert upper_snake("WaitCooking") == "WAIT_COOKING"
    assert upper_snake("0 - not specified") == "V_0_NOT_SPECIFIED"
    assert field_name("from") == "from_"
    assert field_name("json") == "json_"
    assert field_name("modelName") == "model_name_"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/api/1/order/create", ("order", "create")),
        ("/api/2/menu", ("menu",)),
        ("/api/menu/v3/by_id", ("menu", "by_id")),
        ("/api/1/loyalty/iiko/customer/wallet/hold", ("loyalty", "customer", "wallet", "hold")),
        ("/api/finance/v1/cash-flow-category/list", ("finance", "cash_flow_category", "list")),
        ("/api/1/order/init_by_posOrder", ("order", "init_by_pos_order")),
        ("/api/1/request/new", ("request_", "new")),
    ],
)
def test_method_path(url: str, expected: tuple[str, ...]) -> None:
    assert method_path(url) == expected


def test_clean_text() -> None:
    text = "Default: <code>15</code></br>Example: <b>10</b><br />\n> Allowed from version `7.4.6`.<remarks>x</remarks>"
    assert clean_text(text) == "Default: `15`\nExample: **10**\n\nAllowed from version `7.4.6`.\nx"


def test_colliding_schema_names_are_disambiguated() -> None:
    names = assign_names(
        {
            "iikoTransport.PublicApi.Contracts.Deliveries.Request.CreateOrder.Customer",
            "iikoTransport.PublicApi.Contracts.Deliveries.Response.Order.Customer",
            "iikoTransport.PublicApi.Contracts.NomenclatureV3.Combo",
            "iikoTransport.PublicApi.Contracts.Deliveries.Request.CreateOrder.Combo",
            "Unique",
        }
    )
    assert sorted(names.values()) == ["Combo", "Customer", "MenuCombo", "RetrievedCustomer", "Unique"]


def _spec() -> dict[str, Any]:
    return {
        "paths": {
            "/api/1/a": {
                "post": {
                    "tags": ["T"],
                    "summary": "A.",
                    "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Req"}}}},
                    "responses": {"200": {}},
                }
            },
            "/api/1/gone": {"post": {"tags": ["T"], "summary": "Gone.", "responses": {"200": {}}}},
        },
        "components": {
            "schemas": {
                "Req": {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}},
                "Kind": {"type": "string", "enum": ["A", "B"]},
            }
        },
    }


def test_summarize_changes() -> None:
    old = _spec()
    new = copy.deepcopy(old)
    del new["paths"]["/api/1/gone"]
    new["paths"]["/api/1/b/create"] = {"post": {"tags": ["T"], "summary": "Create B.", "responses": {"200": {}}}}
    new["paths"]["/api/1/a"]["post"]["deprecated"] = True
    new["components"]["schemas"]["Req"]["properties"]["comment"] = {"type": "string"}
    new["components"]["schemas"]["Kind"]["enum"].append("C")
    summary = summarize(Spec(old), Spec(new))
    assert "- `/api/1/b/create`: `iiko.b.create()`, Create B." in summary
    assert "- `/api/1/gone` (was `iiko.gone()`)" in summary
    assert "### Newly deprecated endpoints\n\n- `/api/1/a`" in summary
    assert "- `Req`: +`comment`" in summary
    assert "- `Kind`: +'C'" in summary


def test_summarize_no_changes() -> None:
    assert summarize(Spec(_spec()), Spec(_spec())) == "No changes in the iikoCloud API specification."


def _mini_spec(schemas: dict[str, Any], request: str = "Req") -> Spec:
    return Spec(
        {
            "paths": {
                "/api/1/thing": {
                    "post": {
                        "tags": ["T"],
                        "summary": "Thing.",
                        "requestBody": {
                            "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{request}"}}}
                        },
                        "responses": {"200": {}},
                    }
                }
            },
            "components": {"schemas": schemas},
        }
    )


def test_generated_name_clashes_fail_loudly() -> None:
    from codegen.build import build  # noqa: PLC0415

    schemas = {
        "Req": {
            "type": "object",
            "properties": {
                "pay": {"$ref": "#/components/schemas/Pay"},
                "legacy": {"$ref": "#/components/schemas/PayBase"},
            },
        },
        "Pay": {
            "type": "object",
            "properties": {"kind": {"type": "string"}},
            "discriminator": {"propertyName": "kind", "mapping": {"Cash": "#/components/schemas/PayCash"}},
        },
        "PayCash": {"allOf": [{"$ref": "#/components/schemas/Pay"}, {"type": "object", "properties": {}}]},
        "PayBase": {"type": "object", "properties": {"x": {"type": "integer"}}},
    }
    with pytest.raises(ValueError, match=r"clash: \['PayBase'\]"):
        build(_mini_spec(schemas))


def test_unsupported_all_of_fails_loudly() -> None:
    from codegen.build import build  # noqa: PLC0415

    schemas = {
        "Req": {
            "type": "object",
            "properties": {"both": {"allOf": [{"$ref": "#/components/schemas/A"}, {"$ref": "#/components/schemas/B"}]}},
        },
        "A": {"type": "object", "properties": {"a": {"type": "string"}}},
        "B": {"type": "object", "properties": {"b": {"type": "string"}}},
    }
    with pytest.raises(NotImplementedError, match="allOf of 2 schemas"):
        build(_mini_spec(schemas))


def test_awkward_property_names() -> None:
    from codegen.build import build  # noqa: PLC0415

    schemas = {
        "Req": {
            "type": "object",
            "properties": {
                "str": {"type": "string"},
                "datetime": {"type": "string", "format": "date"},
                "example": {"$ref": "#/components/schemas/Hidden"},
            },
        },
        "Hidden": {"type": "object", "properties": {"x": {"type": "integer"}}},
    }
    ir = build(_mini_spec(schemas))
    request = next(m for m in ir.models.values() if m.name == "Req")
    assert [(f.name, f.alias) for f in request.fields] == [
        ("str_", "str"),
        ("datetime_", "datetime"),
        ("example", "example"),
    ]
    assert any(m.name == "Hidden" for m in ir.models.values())  # reached through a property called "example"
