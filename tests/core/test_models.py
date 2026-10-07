from __future__ import annotations

import datetime
import pickle
from decimal import Decimal

import pytest
from pydantic import ValidationError

from iikocloudapi._base import LENIENT_CONTEXT, IikoModel, number_to_json, to_jsonable
from iikocloudapi.models import (
    CashPayment,
    ChangeCompleteBeforeRequest,
    CreateTableOrderRequest,
    DeliveryStatus,
    ExternalDataEntry,
    ExternalPayment,
    ExternalPaymentAdditionalData,
    GetOrganizationsResponse,
    IikoNetUserSex,
    PaymentBase,
    SimpleOrganizationInfo,
    TableOrdersResponse,
    TerminalGroupsResponse,
    UpdateDeliveryStatusRequest,
    UpdateOrderProblemRequest,
)

ORDER = {"organizationId": "o", "terminalGroupId": "t", "order": {"tableIds": ["t1"], "items": []}}


class TestOpenEnums:
    def test_known_values_are_members(self) -> None:
        assert DeliveryStatus("OnWay") is DeliveryStatus.ON_WAY
        assert DeliveryStatus.ON_WAY.is_known

    def test_unknown_values_become_pseudo_members(self) -> None:
        status = DeliveryStatus("Teleported")
        assert status == "Teleported"
        assert not status.is_known
        assert isinstance(status, DeliveryStatus)
        assert pickle.loads(pickle.dumps(status)) == "Teleported"  # noqa: S301

    def test_int_enums_get_names_from_descriptions(self) -> None:
        assert IikoNetUserSex(1) is IikoNetUserSex.MALE
        unknown = IikoNetUserSex(9)
        assert unknown == 9
        assert not unknown.is_known


class TestStrictRequests:
    def test_unknown_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError, match=r"unknown field\(s\): credentials"):
            ExternalPaymentAdditionalData(custom_data="x", credentials="y")  # type: ignore[call-arg]

    def test_unknown_enum_value_is_rejected(self) -> None:
        UpdateDeliveryStatusRequest(organization_id="o", order_id="x", delivery_status="OnWay")  # type: ignore[arg-type]
        with pytest.raises(ValidationError, match="'Teleported' is not a valid DeliveryStatusForUpdate"):
            UpdateDeliveryStatusRequest(organization_id="o", order_id="x", delivery_status="Teleported")  # type: ignore[arg-type]

    def test_unknown_union_variant_is_rejected(self) -> None:
        payment = {"paymentTypeKind": "Bitcoin", "sum": 1, "paymentTypeId": "pt"}
        with pytest.raises(ValidationError, match="'Bitcoin' is not one of"):
            CreateTableOrderRequest.model_validate({**ORDER, "order": {**ORDER["order"], "payments": [payment]}})

    def test_snake_case_and_camel_case_keys(self) -> None:
        a = ExternalDataEntry.model_validate({"key": "k", "value": "v"})
        b = ExternalPayment.model_validate({"payment_type_id": "p", "sum": 1})
        c = ExternalPayment.model_validate({"paymentTypeId": "p", "sum": 1})
        assert a.key == "k"
        assert b == c


class TestLenientResponses:
    def test_unknown_fields_enum_values_and_variants_are_kept(self) -> None:
        body = {
            "correlationId": "c",
            "organizations": [
                {"responseType": "Simple", "id": "1", "name": "A", "isMoonBase": True},
                {"responseType": "Holographic", "id": "2", "name": "B"},
            ],
        }
        result = GetOrganizationsResponse.model_validate(body, context=LENIENT_CONTEXT)
        simple, unknown = result.organizations
        assert isinstance(simple, SimpleOrganizationInfo)
        assert simple.model_extra == {"isMoonBase": True}
        assert type(unknown).__name__ == "OrganizationInfoBase"
        assert unknown.response_type == "Holographic"

    def test_generic_organization_items(self) -> None:
        body = {
            "correlationId": "c",
            "terminalGroups": [
                {"organizationId": "o", "items": [{"id": "t", "organizationId": "o", "name": "T", "timeZone": "UTC"}]}
            ],
            "terminalGroupsInSleep": [],
        }
        result = TerminalGroupsResponse.model_validate(body, context=LENIENT_CONTEXT)
        assert result.terminal_groups[0].items[0].name == "T"


class TestRoundTrip:
    def test_response_models_can_be_sent_back(self) -> None:
        draft = TableOrdersResponse.model_validate(
            {"correlationId": "c", "orders": [], "brandNewServerField": 1}, context=LENIENT_CONTEXT
        )
        assert draft.model_extra == {"brandNewServerField": 1}
        # A response model (with fields unknown to this library) can be passed back into a request model.
        wrapper = Holder(response=draft)
        assert to_jsonable(wrapper)["response"]["brandNewServerField"] == 1

    def test_strictness_is_not_inherited_from_a_response(self) -> None:
        draft = TableOrdersResponse.model_validate({"correlationId": "c", "orders": []}, context=LENIENT_CONTEXT)
        with pytest.raises(ValidationError, match="unknown field"):
            TableOrdersResponse.model_validate({**draft.model_dump(by_alias=True), "typo": 1})


class Holder(IikoModel):
    response: TableOrdersResponse


class TestSerialization:
    def test_discriminator_is_always_sent(self) -> None:
        payment = CashPayment(payment_type_id="p", sum=Decimal("10.10"))
        assert to_jsonable(payment) == {"paymentTypeKind": "Cash", "paymentTypeId": "p", "sum": 10.1}

    def test_explicit_none_is_sent_as_null(self) -> None:
        payment = ExternalPayment(payment_type_id="p", sum=Decimal(1), is_prepay=None)
        assert to_jsonable(payment)["isPrepay"] is None

    def test_base_of_union_is_usable(self) -> None:
        assert issubclass(ExternalPayment, PaymentBase)

    def test_required_nullable_fields_are_always_sent(self) -> None:
        request = UpdateOrderProblemRequest(organization_id="o", order_id="x", has_problem=False)
        assert to_jsonable(request) == {"organizationId": "o", "orderId": "x", "hasProblem": False, "problem": None}

    @pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity", "1E+400"])
    def test_numbers_json_cannot_represent(self, value: str) -> None:
        with pytest.raises(ValueError, match="iikoCloud"):
            number_to_json(Decimal(value))

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (Decimal(2), 2),
            (Decimal("2.50"), 2.5),
            (Decimal("0.1"), 0.1),
            (Decimal("1E+2"), 100),
            (Decimal("1e20"), 1e20),
        ],
    )
    def test_numbers(self, value: Decimal, expected: float) -> None:
        result = number_to_json(value)
        assert result == expected
        assert type(result) is type(expected)

    def test_iiko_datetime(self) -> None:
        request = ChangeCompleteBeforeRequest(
            organization_id="o", order_id="x", new_complete_before=datetime.datetime(2024, 5, 6, 7, 8, 9, 123456)
        )
        assert to_jsonable(request)["newCompleteBefore"] == "2024-05-06 07:08:09.123"
        parsed = ChangeCompleteBeforeRequest.model_validate(
            {"organizationId": "o", "orderId": "x", "newCompleteBefore": "2024-05-06 07:08:09.123"}
        )
        assert parsed.new_complete_before == datetime.datetime(2024, 5, 6, 7, 8, 9, 123000)
