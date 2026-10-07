# Examples

The [`examples/`](https://github.com/tdeni/iikocloudapi/tree/master/examples) directory contains runnable
scripts. They read credentials from environment variables (`IIKO_API_KEY`, `IIKO_APP_ID`, `IIKO_CLIENT_SECRET`, or
`IIKO_API_LOGIN`) and are run against a fake iikoCloud in the test suite, so they always match the current API.

```bash
IIKO_API_KEY=... IIKO_APP_ID=... IIKO_CLIENT_SECRET=... python -m examples.quickstart
```

## Quickstart

Organizations, their terminal groups and whether the terminals are online.

```python
--8<-- "examples/quickstart.py"
```

## Table order, pay first

The guest pays online, and the order reaches the restaurant already paid with an `External` payment.

```python
--8<-- "examples/table_order_pay_first.py"
```

## Table order, cook first

Open an order (or add to the one already open on the table), pay with funds held by the acquirer, close it.

```python
--8<-- "examples/table_order_cook_first.py"
```

## Delivery

A delivery order paid in cash on delivery.

```python
--8<-- "examples/delivery.py"
```

## Menu sync

An external menu (v3) with stop list marks.

```python
--8<-- "examples/menu_sync.py"
```

## Webhook receiver

A FastAPI application that receives and dispatches webhook events, and the code that registers it.

```python
--8<-- "examples/webhook_receiver.py"
```
