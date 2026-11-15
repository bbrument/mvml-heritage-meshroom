#!/usr/bin/env python
"""Load Meshroom templates/projects; report CompatibilityNodes, and the node versions recorded in the file header
against the installed node descriptions.
Usage (Meshroom environment set, see docs/INSTALL.md): python check_templates.py <file.mgt|file.mg> [...]   Exit 1 if any CompatibilityNode.
With the Meshroom nightly bundle, run it with the Python of the bundle (docs/INSTALL.md, step 5)."""
import json
import sys

import meshroom
# as meshroom_batch does: with MESHROOM_INSTALL_DIR (nightly bundle), sets the AliceVision nodes, templates and
# variables of the bundle; no effect on an install from source
meshroom.setupEnvironment()
import meshroom.core  # noqa: E402
from meshroom.core.graph import loadGraph  # noqa: E402


def main():
    meshroom.core.initPlugins()
    meshroom.core.initNodes()
    failed = False
    for path in sys.argv[1:]:
        data = json.load(open(path)); header = data.get("header", {})
        g = loadGraph(path)
        issues = [f"{n.name} ({n.nodeType} {n.issue.name})" for n in g.nodes if n.isCompatibilityNode]
        failed |= bool(issues)
        print(f"{'FAIL' if issues else 'OK  '} {path}: {len(g.nodes)} nodes" + (", " + ", ".join(issues) if issues else ""))
        print(f"     header: releaseVersion {header.get('releaseVersion')}, fileVersion {header.get('fileVersion')}")
        recorded = header.get("nodesVersions", {})
        descs = header.get("nodeDescriptions", {})
        providers = meshroom.core.pluginManager.getNodeDescProviders()
        for nodeType in sorted({n.nodeType for n in g.nodes}):
            prov = providers.get(nodeType)
            installed = meshroom.core.nodeVersion(prov.nodeDescClass) if prov else None
            plugin = f"{prov.plugin.name} {getattr(prov.plugin, 'version', '?')}" if prov else "absent"
            rec = recorded.get(nodeType) or next((v.get("version") for v in data.get("graph", {}).values() if v.get("nodeType") == nodeType and v.get("version")), None)
            if rec is None or str(rec) != str(installed):
                print(f"     != {nodeType}: template {rec} / installed {installed} ({plugin})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
