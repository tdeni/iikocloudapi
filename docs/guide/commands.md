# Asynchronous commands

Endpoints that change orders (create, add items, pay, close, cancel...) are **commands**: iikoCloud accepts the
request, returns a `correlation_id` immediately and delivers the change to the restaurant's terminal in the
background. Whether the command succeeded is reported by `/api/1/commands/status`. Commands are marked in the
[coverage table](../reference/index.md) and in the method documentation.

`iiko.wait()` polls the status with a growing interval until the command finishes:

```python
from iikocloudapi import CommandFailed, CommandTimeout

created = await iiko.order.create(organization_id=org_id, terminal_group_id=group_id, order=order)
try:
    await iiko.wait(created, organization_id=org_id, timeout=60)
except CommandFailed as error:
    print("Rejected by the terminal:", error.exception, error.error_reason)
except CommandTimeout:
    print("Still in progress; check again later with iiko.commands.status()")
```

`wait()` accepts the command's response or its `correlation_id` string. It returns `SuccessCommandStatus`.

Things to keep in mind:

- The `correlation_id` belongs to an organization; pass the same `organization_id` you used for the command.
- Status information is kept for a limited time; asking about an old command raises `Gone`.
- `CommandTimeout` does not mean the command failed. The terminal may be offline and process it later; use
  `iiko.terminal_groups.is_alive()` to check, and webhooks to learn about the outcome without polling.
