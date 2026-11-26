"""
kernel_path.py: the kernel's models, imported in place from formal/vendor/kernel (kernel-v0.4.0, held to their hashes
by tools/vendor_models.py --check). Importing this module puts on sys.path what those files expect beside them in the
kernel's own layout: this directory (causal_kernel, cut, checkpoint, route, ...), formal/kernel_lib (the kernel's
models/kernel_lib) and formal/roster_fork (its models/roster_fork). The one file they open by path,
formal/data/governance_policy.json, is a link to manifests/governance_policy.json.

python3 -I kernel_path.py check_rosters [args]   runs a vendored check, its expected table read from this directory
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORMAL = os.path.dirname(HERE)
KERNEL = os.path.join(FORMAL, "vendor", "kernel")
for p in (os.path.join(FORMAL, "roster_fork"), os.path.join(FORMAL, "kernel_lib"), HERE, KERNEL):
    if p not in sys.path: sys.path.insert(0, p)

if __name__ == "__main__":
    import importlib
    mod = importlib.import_module(sys.argv[1])
    assert os.path.dirname(os.path.abspath(mod.__file__)) == KERNEL, mod.__file__
    mod.HERE = HERE      # the expected tables are this repository's, kept here
    sys.argv = [mod.__file__] + sys.argv[2:]
    sys.exit(mod.main())
