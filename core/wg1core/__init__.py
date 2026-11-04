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
