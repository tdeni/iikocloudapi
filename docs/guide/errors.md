# Errors

All exceptions raised by the library derive from `IikoError`:

| Exception | Raised when |
| --- | --- |
| `IikoNetworkError` | the connection failed, timed out or broke |
| `IikoApiError` | iikoCloud answered with an error status, base class of the following |
| `BadRequest` | 400 |
| `Unauthorized` | 401 |
| `Forbidden` | 403 |
| `NotFound` | 404 |
| `RequestTimeout` | 408, the terminal did not answer within the `Timeout` header |
| `Conflict` | 409 |
| `Gone` | 410, for example an expired correlation ID |
| `UnprocessableEntity` | 422 |
| `TooManyRequests` | 429, see `retry_after` |
| `ServerError` | 5xx |
| `ResponseValidationError` | the response does not match the model |
| `CommandFailed` | an asynchronous command finished with an error |
| `CommandTimeout` | an asynchronous command did not finish in time (also a `TimeoutError`) |

Invalid *arguments* raise `pydantic.ValidationError` before anything is sent.

`IikoApiError` understands both error formats used by iikoCloud and exposes the details:

```python
from iikocloudapi import BadRequest, IikoApiError, TooManyRequests

try:
    await iiko.deliveries.create(organization_id=org_id, terminal_group_id=group_id, order=order)
except BadRequest as error:
    print(error.description)  # human-readable text from iikoCloud
    print(error.error)  # short error code, if any
    print(error.correlation_id)  # quote it when contacting iiko support
except TooManyRequests as error:
    await asyncio.sleep(error.retry_after or 1)
except IikoApiError as error:
    print(error.status_code, error.response.text)
```

## Retries

The library does not retry failed requests (except once after `401`, see
[Authentication](authentication.md)). Many endpoints are not idempotent: retrying `order/create` after a timeout
may create a second order. If you retry, make the operation idempotent first, for example by passing your own
`id` for the new order and checking with `order.by_id()` before creating it again.
