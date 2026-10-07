# Changelog

All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

---
## [1.0.0](https://github.com/tdeni/iikocloudapi/compare/v0.4.1..v1.0.0) - 2026-10-08

A rewrite: the client is now generated from the iikoCloud OpenAPI specification.
See the [migration guide](https://tdeni.github.io/iikocloudapi/migration/).

### Features

- All 324 current endpoints of the iikoCloud API, including deliveries, reserves, loyalty, inventory, finance,
  nomenclature, employees, reports and webhooks settings; method names mirror the URLs
- `IikoCloud` client with `async with`, `request()` for raw calls and `wait()` for asynchronous commands
- `AppAuth` for `/api/v2/access_token`; `ApiLoginAuth` keeps the deprecated `/api/1/access_token` working
- Typed error hierarchy (`BadRequest`, `Unauthorized`, `TooManyRequests`, `CommandFailed`, ...) for both error
  formats used by iikoCloud
- Models for every request and response: strict when built, lenient when parsed (unknown fields, enum values and
  union variants are preserved); all numbers are `Decimal`
- Webhook event models, `parse_webhook()` and `verify_webhook_token()`
- Documentation site, runnable examples, weekly specification updates
- Support for Python 3.12, 3.13 and 3.14 (including free-threaded 3.14)

### Bug Fixes

- Clients created with different API logins shared one token through mutable default headers
- Stop list items were sent in `snake_case` and failed to serialize `Decimal` balances
- Order types were requested from a wrong URL
- The HTTP timeout (5 s) was shorter than the server-side `Timeout` header (15 s)
- The retry after `401` dropped the HTTP method; non-JSON error bodies raised `JSONDecodeError`

### Upgrade

- `httpx` replaced by its maintained continuation `httpx2`; `orjson` is no longer needed
- pydantic 2.13

---
## [0.4.1](https://github.com/tdeni/iikocloudapi/compare/v0.4.0..v0.4.1) - 2025-06-05

### Bug Fixes

- returns available to api-login user organizations specified settings method - ([dfc6e1f](https://github.com/tdeni/iikocloudapi/commit/dfc6e1f34d6b556eeb37dd8cfea557c738b2361e)) - Deni Tazurkaev

### Miscellaneous Chores

- fix README.md - ([bd7b80a](https://github.com/tdeni/iikocloudapi/commit/bd7b80a73ec30c0818c7a2c07d4c883ed517bb66)) - Deni Tazurkaev

### Upgrade

- pydantic & orjson (and dev dependencies) - ([582bb07](https://github.com/tdeni/iikocloudapi/commit/582bb07cd5feaa5ca1cc1f3e32c9bb1754780fec)) - Deni Tazurkaev

---
## [0.4.0](https://github.com/tdeni/iikocloudapi/compare/v0.3.1..v0.4.0) - 2025-03-28

### Bug Fixes

- headers for every request - ([cf286a4](https://github.com/tdeni/iikocloudapi/commit/cf286a4d25fe9f8f14c5ee478dd7a6a1427ee059)) - Deni Tazurkaev
- retrieve external menu by ID response schema - ([e351983](https://github.com/tdeni/iikocloudapi/commit/e351983a8f82c54d7f778f38e283862e37ccb2e9)) - Deni Tazurkaev

### Documentation

- add module methods api ref - ([2451e0a](https://github.com/tdeni/iikocloudapi/commit/2451e0acc7cbcde732d9b449ccdebd925ab96e03)) - Deni Tazurkaev

### Features

- add operations module - ([55d4263](https://github.com/tdeni/iikocloudapi/commit/55d4263bed6a7c357b562fe35a1769c25189afb8)) - Deni Tazurkaev

### Miscellaneous Chores

- code style - ([5a56797](https://github.com/tdeni/iikocloudapi/commit/5a56797b7498f101358278e8f042671c6f890a20)) - Deni Tazurkaev

### Refactoring

- add organization_ids property - ([328225f](https://github.com/tdeni/iikocloudapi/commit/328225fec5988a1a68cfc35454e7d0d618f13ef6)) - Deni Tazurkaev

---
## [0.3.1](https://github.com/tdeni/iikocloudapi/compare/v0.3.0..v0.3.1) - 2025-03-26

### Miscellaneous Chores

- update package meta - ([468cd6a](https://github.com/tdeni/iikocloudapi/commit/468cd6ada9177e1e7fe7e75aa880c707b00ba428)) - Deni Tazurkaev
- add linter rules, minor fixes - ([72d6d9d](https://github.com/tdeni/iikocloudapi/commit/72d6d9d8d5e414391d3bd299505c791bd66726d6)) - Deni Tazurkaev

---
## [0.3.0](https://github.com/tdeni/iikocloudapi/compare/v0.2.0..v0.3.0) - 2025-03-20

### Bug Fixes

- pass timeout arg in organizations module - ([2b6204e](https://github.com/tdeni/iikocloudapi/commit/2b6204e30218a57f6f14180bdbde9851856724ca)) - Deni Tazurkaev
- move terminal group - ([4611442](https://github.com/tdeni/iikocloudapi/commit/4611442ddcf2cf35ec523bf0d9bf36b8b23280a4)) - Deni Tazurkaev

### Features

- add terminal group module - ([c06dadd](https://github.com/tdeni/iikocloudapi/commit/c06daddf994fb3c122c47bd9f6bd234a57db6c18)) - Deni Tazurkaev
- add dictionaries module - ([f820927](https://github.com/tdeni/iikocloudapi/commit/f8209278efc27ad6fa60996ed7d98bd8f4138270)) - Deni Tazurkaev
- add menu module - ([88c3d12](https://github.com/tdeni/iikocloudapi/commit/88c3d125ebbdce26b6d78a79e162b6436525761b)) - Deni Tazurkaev

---
## [0.2.0](https://github.com/tdeni/iikocloudapi/compare/v0.1.0..v0.2.0) - 2025-03-16

### Features

- auth module - ([166dfe0](https://github.com/tdeni/iikocloudapi/commit/166dfe0d28c2a98cdbd31fb90f7cb59b0308b8df)) - Deni Tazurkaev

### Miscellaneous Chores

- code style - ([873a344](https://github.com/tdeni/iikocloudapi/commit/873a344a1f74d7e17e5e54c2c6e7850e9d71f318)) - Deni Tazurkaev
- maintaining - ([05c33f9](https://github.com/tdeni/iikocloudapi/commit/05c33f94390364deb26a9befb38d47a1e8516169)) - Deni Tazurkaev

<!-- generated by git-cliff -->
