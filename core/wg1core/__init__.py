"""The core of SCE Working Group 1's apparatus: what every canonical model's repository shares.

- `runner`: runs every toolkit on an experiment through its adapter, on the host or under the container contract,
  verifies the results and registers the records; the `wg1core` command.
- `records`: the execution and build records of the run registry, read from git, the machine and the job.
- `canonical`: the strict YAML subset of the parameter, request and experiment files, their canonical serialization
  and the hash that identifies a model.
- `laws`: the shock laws a parameter file states, with their moments in closed form.
- `experiment`: experiment files, and what their validator cannot say about them.
- `schemas/`: the validators of an experiment file, of an execution record, and of a model repository's registry entry.
"""

VERSION = "0.1.0"


def identity() -> dict:
    """The core's name, version and, when it was installed from git, the commit it was installed from, read from the
    installation's direct_url.json (PEP 610); the version alone does not identify a development commit."""
    out = {"name": "wg1core", "version": VERSION}
    try:
        import json
        from importlib import metadata
        text = metadata.distribution("wg1-core").read_text("direct_url.json")
        commit = (json.loads(text).get("vcs_info") or {}).get("commit_id") if text else None
        if commit:
            out["commit"] = commit
    except Exception:  # not installed as a distribution, or no direct_url.json: the version stands alone
        pass
    return out
