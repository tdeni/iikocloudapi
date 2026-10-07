# Development

## Setup

```bash
poetry install --all-groups
```

## Layout

- `spec/iiko-cloud-api.json`: snapshot of the iikoCloud OpenAPI specification.
- `codegen/`: the code generator, not shipped with the package.
- `iikocloudapi/`: the package. `_client.py`, `_auth.py`, `_errors.py`, `_base.py` and the other underscore modules
  are written by hand; `models/` (request and response models, one module per API section) and `resources/`
  (endpoint methods, one module per top-level URL segment) are generated.
- `docs/`: this documentation; `docs/reference/` is generated.
- `examples/`: runnable examples, run by the tests.
- `tests/contract/`: every endpoint checked against the specification.
- `tests/core/`: the hand-written runtime.

Never edit generated files by hand: change the generator or the runtime and regenerate.

## Code generation

```bash
# regenerate from spec/iiko-cloud-api.json
python -m codegen
# download the latest specification, print what changed and regenerate
python -m codegen --fetch
# fail if the generated files are out of date (CI runs this)
python -m codegen --check
```

The generator also updates the coverage table in `README.md` and the reference section of `mkdocs.yml`.

How the specification maps to code:

- **Methods.** Every `POST` endpoint becomes a method whose attribute path is the URL without `/api/` and the
  version (`codegen.spec.method_path`). Deprecated endpoints are dropped when a newer endpoint has the same method
  name, otherwise they are kept and emit `DeprecationWarning`.
- **Models.** Every schema reachable from an endpoint or a webhook becomes a class in the module of the
  `x-tagGroups` group that uses it, or in `common` if several groups do. Schema names are shortened to their last
  segment; collisions are resolved by a namespace prefix (`Retrieved*` for response variants of request models,
  `Menu*` for menu v3) or by `codegen/overrides.py`. If the generator reports an ambiguous name, add it there.
- **Polymorphism.** Schemas with a `discriminator` become a base class (`PaymentBase`), one subclass per variant
  and a tagged union alias (`Payment`) that falls back to the base class for unknown variants.
- **Types.** Numbers become `Decimal`, `yyyy-MM-dd HH:mm:ss.fff` strings become `IikoDateTime`, enums become
  `OpenStrEnum`/`OpenIntEnum` (member names of integer enums are recovered from field descriptions).
- **Required nullable fields** default to `None` and are always sent (`__always_sent__`).

## Checks

```bash
ruff format --check . && ruff check .
pyright
pytest --cov
python -m codegen --check
mkdocs build --strict
```

The contract tests synthesise every request and response from the specification (all variants of polymorphic
objects, with all fields and with required fields only) and check that responses parse without leftovers and that
request bodies round-trip and validate against the specification's JSON Schema.

## Specification updates

The `spec-update` workflow runs every Monday. If the specification changed, it regenerates the package and opens a
pull request whose description lists new, removed and deprecated endpoints and changed schemas. Review it like any
other change: new endpoints are ready to use, removed fields or endpoints are breaking changes for users.

Pull requests created with the default `GITHUB_TOKEN` do not trigger other workflows, so CI does not run on them
automatically. Add a fine-grained personal access token (or a GitHub App token) with *contents* and *pull requests*
write access as the `SPEC_UPDATE_TOKEN` repository secret to get CI on these pull requests.

## Releases

1. Update `version` in `pyproject.toml` and add a section to `CHANGELOG.md`
   (`git cliff --unreleased --tag vX.Y.Z --prepend CHANGELOG.md`).
2. Merge to `master`, then push a tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. The `release` workflow builds the package, checks that the tag matches the version, publishes to PyPI with
   [trusted publishing](https://docs.pypi.org/trusted-publishers/) and creates a GitHub release.

One-time setup: on PyPI, add a trusted publisher for the `iikocloudapi` project with owner `tdeni`,
repository `iikocloudapi`, workflow `release.yml` and environment `pypi`. Enable GitHub Pages with
"GitHub Actions" as the source for the documentation site.
