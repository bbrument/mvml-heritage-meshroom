#!/usr/bin/env python
"""Workaround for B14 (docs/KNOWN_ISSUES.md): insert a ConvertSfMFormat node (.sfm JSON) between the node feeding
LedGetterLights and LedGetterPS and these two nodes, so that the LED-getter nodes do not read the SfMData through the
AliceVision Python bindings.

Needed when the bindings of the AliceVision build were compiled against numpy 1 (the official nightly bundle, November
2026): the mrLedGetter environment has numpy 2 and its nodes then fail with "A module that was compiled using NumPy 1.x
cannot be run in NumPy 2.x", followed by a JSONDecodeError.

Usage (Meshroom environment set, see docs/INSTALL.md):
    python add_convert_sfm.py <project.mg>      # keeps a copy <project>.orig.mg
"""
import shutil
import sys

import meshroom.core
from meshroom.core.graph import loadGraph


def main():
    path = sys.argv[1]
    meshroom.core.initPlugins()
    meshroom.core.initNodes()
    graph = loadGraph(path)
    ledNodes = [n for n in graph.nodes if n.nodeType in ("LedGetterLights", "LedGetterPS")]
    if not ledNodes:
        print(f"{path}: no LED-getter node, unchanged")
        return
    source = ledNodes[0].inputSfm._getInputLink()
    if source is None:
        sys.exit(f"{path}: {ledNodes[0].name}.inputSfm is not connected")
    shutil.copy(path, path.replace(".mg", ".orig.mg"))
    sfmNodes = [n for n in graph.nodes if n.nodeType == "StructureFromMotion"]
    convert = graph.addNewNode("ConvertSfMFormat")
    graph.addEdge(source, convert.input)
    convert.fileExt.value = "sfm"
    if sfmNodes:
        convert.describerTypes.value = list(sfmNodes[0].describerTypes.value)
    for node in ledNodes:
        if node.inputSfm._getInputLink() is source:
            graph.removeEdge(node.inputSfm)
            graph.addEdge(convert.output, node.inputSfm)
    graph.save(path)
    print(f"{path}: {convert.name} added between {source.fullName} and {', '.join(n.name for n in ledNodes)}")


if __name__ == "__main__":
    main()
