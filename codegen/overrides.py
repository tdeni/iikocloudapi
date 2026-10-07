"""Hand-picked names that the generic naming rules can't get right.

Keys are component schema keys from the specification, values are Python class names.
The generator fails loudly if two schemas still end up with the same name.
"""

from __future__ import annotations

# Module (``iikocloudapi.models.<module>``) for every ``x-tagGroups`` group.
GROUP_MODULES: dict[str, str] = {
    "General": "general",
    "Delivery": "delivery",
    "Orders": "orders",
    "Reserves": "reserves",
    "WebHooks": "webhooks",
    "Licenses": "licenses",
    "Loyalty and discounts": "loyalty",
    "Inventory": "inventory",
    "Finance": "finance",
    "Nomenclature": "nomenclature",
    "Employees": "employees",
    "Reports": "reports",
    "Terminals": "terminals",
    "Platform": "platform",
}

# Prefix used for a colliding schema from the given namespace (last dotted segment).
NAMESPACE_PREFIXES: dict[str, str] = {
    "NomenclatureV3": "Menu",
    "Nomenclature": "Nomenclature",
    "LoyaltyResult": "Loyalty",
    "Reserves": "Reserve",
    "DeliveryRestrictions": "Restriction",
    "Address": "Address",
    "Employees": "Employees",
    "PaymentTypes": "",
    "CancelCauses": "",
    "MarketingSources": "",
    "RemovalTypes": "",
    "TipsTypes": "",
    "OrderTypes": "",
    "Errors": "Transport",
}

_T = "iikoTransport.PublicApi.Contracts."

SCHEMA_NAMES: dict[str, str] = {
    f"{_T}Deliveries.Common.OrderServiceType": "OrderServiceType",
    f"{_T}Deliveries.Request.CreateOrder.OrderServiceType": "DeliveryServiceType",
    f"{_T}OrderTypes.OrderServiceType": "OrderTypeServiceType",
    f"{_T}Deliveries.Common.PaymentTypeKind": "PaymentTypeKind",
    f"{_T}PaymentTypes.PaymentTypeKind": "PaymentTypeCategory",
    f"{_T}PaymentTypes.PaymentType": "PaymentType",
    "PaymentType": "InventoryPaymentType",
    f"{_T}NomenclatureV3.AllergenGroup": "MenuAllergenGroup",
    f"{_T}NomenclatureV3.TaxCategory": "MenuTaxCategory",
    f"{_T}Deliveries.Common.Coordinates": "Coordinates",
    f"{_T}Common.ExternalData": "ExternalDataEntry",
    f"{_T}Common.PriceCategory": "PriceCategory",
    f"{_T}Address.Street": "Street",
    f"{_T}Deliveries.Request.CreateOrder.Street": "DeliveryStreet",
    "internal_finance_cashflowcategories.Filter": "CashFlowCategoryFilter",
    "internal_finance_accounts.Filter": "AccountFilter",
    "internal_employees.Filter": "EmployeeFilter",
}
