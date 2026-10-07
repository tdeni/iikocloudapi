# Client

::: iikocloudapi.IikoCloud
    options:
      members: [request, wait, aclose]
      show_root_heading: true
      heading_level: 2

## Authentication

::: iikocloudapi.AppAuth
    options:
      heading_level: 3
      show_root_heading: true

::: iikocloudapi.ApiLoginAuth
    options:
      heading_level: 3
      show_root_heading: true

::: iikocloudapi.IikoAuth
    options:
      heading_level: 3
      show_root_heading: true
      members: [token_request, parse_token_response, token, invalidate]

## Errors

::: iikocloudapi._errors
    options:
      show_root_heading: false
      heading_level: 3
      members_order: source
      filters: ['!^_', '!^error_from_response$']

## Webhooks

::: iikocloudapi.webhooks
    options:
      show_root_heading: false
      heading_level: 3
      members: [parse_webhook, verify_webhook_token]

## Types

::: iikocloudapi._base
    options:
      show_root_heading: false
      heading_level: 3
      members: [IikoModel, OpenStrEnum, OpenIntEnum, IikoDateTime, IsoDateTime, OrganizationItems]
