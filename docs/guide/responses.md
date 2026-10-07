# Responses and models

Every method returns a model from `iikocloudapi.models` (or a list of models, or `None` for endpoints without a
response body). Attributes are `snake_case`; `model_dump(by_alias=True)` gives back the original `camelCase` JSON.

```python
response = await iiko.payment_types(organization_ids=[org_id])
for payment_type in response.payment_types:
    print(payment_type.name, payment_type.payment_type_kind)
```

## Forward compatibility

iikoCloud adds fields and enum values without changing the API version. Responses are parsed leniently, so your
code keeps working:

**Unknown fields** are kept in `model_extra`:

```python
response.model_extra  # {"someNewField": ...}
```

**Unknown enum values** become pseudo-members. They compare equal to the raw string and have `is_known == False`:

```python
status = order.status  # DeliveryStatus
status == "OnWay"  # True for known and unknown values alike
status.is_known  # False if iikoCloud sent a value this version does not know
```

**Unknown variants** of polymorphic objects are parsed as the base model, so you can still read the common fields:

```python
from iikocloudapi.models import ErrorCommandStatus, SuccessCommandStatus

match await iiko.commands.status(organization_id=org_id, correlation_id=correlation_id):
    case SuccessCommandStatus():
        ...
    case ErrorCommandStatus(exception=exception):
        ...
    case other:  # InProgressCommandStatus or a state added later
        ...
```

## Required fields

Fields the specification marks as required are required in the models. If iikoCloud ever omits one, the method
raises [`ResponseValidationError`](errors.md) with the raw response attached, instead of returning a half-empty
object.

## Organization-scoped lists

Several endpoints group results by organization. They use the generic `OrganizationItems[T]` model:

```python
groups = await iiko.terminal_groups(organization_ids=[org_id])
for organization in groups.terminal_groups:  # list[OrganizationItems[TerminalGroup]]
    print(organization.organization_id, [group.name for group in organization.items])
```
