# Earlier drafts of the registry schema

The drafts of the registry schema that a published core wrote records under, kept so that the status reader
(`../../status.py`) checks a record against the draft it names in its `$schema`, not against the core's own draft,
which an earlier record was never meant to match. Each file is copied from git unchanged, as the draft last stood. The
core's own drafts are the two files in the folder above.

| file | identifier | taken from |
|---|---|---|
| `runs.registry-0.1.0-draft.7.json` | `econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.7.json` | 6c12de1, the draft's last form |
| `runs.registry-0.1.0-draft.6.json` | `econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.6.json` | ee85a8f |
| `runs.registry-0.1.0-draft.5.json` | `econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.5.json` | ea5de86 |
| `runs.registry-0.1.0-draft.4.json` | `econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.4.json` | b85282c |
| `fork-runs.registry-0.1.0-draft.4.json` | `llorracc/sce-wg-1-dev/harness/runs.registry/0.1.0-draft.4.json` | 5c6961b, `harness/runs.registry.schema.json` |
| `fork-execution-record-0.1.0-draft.4.json` | `llorracc/sce-wg-1-dev/harness/execution-record/0.1.0-draft.4.json` | 5c6961b, `harness/execution-record.schema.json` |

The four drafts under the working group's identifier refer to the execution-record schema's draft 4, which is still
the core's own. The two files named `fork-` are the harness's, from before the core was a package, when the
identifiers named the fork; the buffer-stock model's first registered run names them. Identifiers are given here without `https://github.com/`.
