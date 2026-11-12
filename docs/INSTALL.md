# Installation

How to set up Meshroom, AliceVision and the plugins needed by the [templates](TEMPLATES.md), on Linux, from the
command line. This is the setup of the [tested versions](TESTED_VERSIONS.md) (November 2026). The templates need the
**develop** branch of Meshroom: no Meshroom release can open them yet.

> [!IMPORTANT]
> The plugin manager of Meshroom develop still lacks five fixes, open as pull requests
> ([#3256](https://github.com/alicevision/Meshroom/pull/3256) to
> [#3260](https://github.com/alicevision/Meshroom/pull/3260)). Merge them locally (step 2), or install the RNb-NeuS2
> testbed by hand (step 5). mrSegmentation is not in the official plugin registry yet
> ([mrSegmentation#85](https://github.com/meshroomHub/mrSegmentation/pull/85)): a registry file of this repository
> adds it (step 4). This page will get shorter as these changes are merged.

Contents: [Requirements](#requirements) · [1. AliceVision](#1-alicevision) · [2. Meshroom](#2-meshroom) ·
[3. Environment](#3-environment) · [4. Plugins](#4-plugins) · [5. RNb-NeuS2 testbed](#5-rnb-neus2-testbed) ·
[6. SAM 3 checkpoint](#6-sam-3-checkpoint) · [7. Check](#7-check)

## Requirements

| | |
| :-- | :-- |
| OS | Linux x86_64, glibc 2.34 or newer (tested: Ubuntu 22.04) |
| GPU | NVIDIA, 16 GB (the low-resolution runs peak at 11-13 GB); **compute capability 8.0 or newer for LINO-UniPS** ([R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere)); driver supporting CUDA 12 (570 or newer for RTX 50xx) |
| Disk | about 30 GB for the plugins (27 GB for the four plugins of the tested runs) and 3.5 GB for the SAM 3 checkpoint, plus the projects |
| Tools | `git`, [`uv`](https://docs.astral.sh/uv/getting-started/installation/), a [Hugging Face](https://huggingface.co) account |
| System libraries | `libusb-1.0` (Open3D, [B15](KNOWN_ISSUES.md#other-issues)); for the UI: `libOpenGL`, `libEGL`, `libxcb-cursor` |

## 1. AliceVision

Either take the nightly build of AliceVision, or build it from source.

**Nightly build.** Download `AliceVision-nightly-<date>-<commit>-linux.tar.gz` (and `qtAliceVision-nightly-…` for the
UI) from the [nightly release](https://github.com/alicevision/AliceVision/releases/tag/nightly) and extract them. Two
things are missing from the November 2026 nightly and must be added by hand:

- the USD resources (`lib64/usd/**/plugInfo.json`), without which every `.usda` export (StructureFromMotion,
  ExportImages) stops with `Failed to find the plugInfo.json file that declares the plugin for ArDefaultResolver`
  ([B9](KNOWN_ISSUES.md#other-issues)): copy `lib/usd/` of the matching
  [AliceVision dependencies](https://github.com/alicevision/AliceVisionDependencies) (USD 26.8) into `lib64/usd/`;
- the vocabulary tree and the detection models ([B13](KNOWN_ISSUES.md#other-issues)): `vlfeat_K80L3.SIFT.tree`
  (ImageMatching fails beyond 200 images without it), `sphereDetection_Mask-RCNN.onnx`, `fcn_resnet50.onnx` and
  `ColorChartDetectionModel/`, for instance from the `aliceVision/share/aliceVision/` folder of the
  [Meshroom 2025.1.0 release](https://github.com/alicevision/Meshroom/releases/tag/v2025.1.0).

**From source.** Follow the [AliceVision build instructions](https://github.com/alicevision/AliceVision/blob/develop/INSTALL.md)
on the develop branch (tested: [`6f9f58ec`](https://github.com/alicevision/AliceVision/commit/6f9f58ec)). Build the
Python bindings (`pyalicevision`) against numpy 2 headers: they then work with both numpy 1 and numpy 2, which avoids
[B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error).

## 2. Meshroom

Clone the develop branch and merge the five open pull requests of the plugin manager (they merge without conflict on
develop of 2026-11-12, `de4b5661`):

```bash
git clone https://github.com/alicevision/Meshroom.git
cd Meshroom
git checkout -b visart develop
for n in 3256 3257 3258 3259 3260; do
    git fetch origin pull/$n/head:pr$n && git merge --no-ff --no-edit pr$n
done
```

Create the Python environment of Meshroom with the Python of AliceVision (3.11; the nightly bundle ships it as
`python/bin/python3.11`):

```bash
/path/to/AliceVision/python/bin/python3.11 -m venv ../meshroom-venv
../meshroom-venv/bin/pip install -r requirements.txt -r dev_requirements.txt
```

The plugins build their own environments with `uv` and the Python that runs Meshroom: keep the same Python for all.

## 3. Environment

Save this as `env.sh`, adapt the paths, and source it before any Meshroom command:

```bash
AV=/path/to/AliceVision                   # nightly bundle or install folder
MR=/path/to/Meshroom                      # clone of step 2
VENV=/path/to/meshroom-venv
export ALICEVISION_ROOT=$AV
# start from an empty LD_LIBRARY_PATH: a CUDA toolkit path (e.g. /usr/local/cuda/lib64 added by ~/.bashrc) hides the
# CUDA libraries of the plugin wheels
export LD_LIBRARY_PATH=$AV/lib64:$AV/lib
export PATH=$VENV/bin:$AV/bin:/usr/local/bin:/usr/bin:/bin
export PYTHONPATH=$MR:$AV/lib64/python
export ALICEVISION_SENSOR_DB=$AV/share/aliceVision/cameraSensors.db
export ALICEVISION_VOCTREE=$AV/share/aliceVision/vlfeat_K80L3.SIFT.tree
export ALICEVISION_SPHERE_DETECTION_MODEL=$AV/share/aliceVision/sphereDetection_Mask-RCNN.onnx
export ALICEVISION_COLORCHARTDETECTION_MODEL_FOLDER=$AV/share/aliceVision/ColorChartDetectionModel
export MESHROOM_NODES_PATH=$AV/share/meshroom
export MESHROOM_PIPELINE_TEMPLATES_PATH=$AV/share/meshroom
# installed plugins and registry files; do NOT create this folder beforehand: Meshroom copies the official registry
# into it only when it does not exist
export MESHROOM_LOCAL_PLUGINS_PATH=/path/to/meshroom-plugins
export RDS_SAM3_MODEL_PATH=/path/to/sam3.pt   # step 6
```

For the UI, add `export QML2_IMPORT_PATH=<qtAliceVision>/qml QT_PLUGIN_PATH=<qtAliceVision>` and run
`python $MR/meshroom/ui`.

## 4. Plugins

| Plugin | Needed by | Version tested |
| :-- | :-- | :-- |
| [mrLedGetter](https://github.com/meshroomHub/mrLedGetter) | `[object]_visart-eccv26.mgt` of warrior, biface, calathos; `gourdan_bone_led_getter.mgt` | v1.0.2 |
| [mrLINOUniPS](https://github.com/meshroomHub/mrLINOUniPS) | `[object]_lino_unips.mgt` | v2.0.4 |
| [mrUniMSPS](https://github.com/meshroomHub/mrUniMSPS) | `gourdan_bone_visart-eccv26.mgt` | v2.0.4 (not run end to end, see [tested versions](TESTED_VERSIONS.md)) |
| [mrRNbNeuS2](https://github.com/meshroomHub/mrRNbNeuS2) | all templates | v1.1.2 |
| [mrSegmentation](https://github.com/meshroomHub/mrSegmentation) | all templates (SAM 3 masks) | head of PR #85, `976a63b` |

Install them with the plugin manager, from the command line (`-f` answers its questions; without it, it fails with
`EOFError` when there is no terminal) or from *Manage Plugins* in the UI:

```bash
source env.sh
python $MR/bin/meshroom_plugins list            # first call: creates $MESHROOM_LOCAL_PLUGINS_PATH
# mrSegmentation is not in the official registry yet: add the registry file of this repository
cp /path/to/visart-eccv26/registry/visartSegmentation.json $MESHROOM_LOCAL_PLUGINS_PATH/
for p in mrLedGetter mrLINOUniPS mrUniMSPS mrRNbNeuS2 mrSegmentation; do
    python $MR/bin/meshroom_plugins install -f $p
done
```

Expect about one hour for mrSegmentation and 5-20 minutes for each of the others (PyTorch and JAX wheels).

Then fix the environment of mrSegmentation, which does not declare OpenImageIO
([R4](KNOWN_ISSUES.md#r4-mrsegmentation-no-module-named-openimageio)). The bounds keep numpy 1, needed by the
AliceVision bindings; redo it after any `update` of the plugin:

```bash
uv pip install --python $MESHROOM_LOCAL_PLUGINS_PATH/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
```

## 5. RNb-NeuS2 testbed

With the pull requests of step 2, the plugin manager downloads and extracts the compiled RNb-NeuS2 testbed with
mrRNbNeuS2. Without them, it prints a warning about the `testbed` asset: then extract the archive of the
[RNb-NeuS2 v2.0.3 release](https://github.com/RobinBruneau/RNb-NeuS2/releases/tag/v2.0.3) by hand, as described in the
[mrRNbNeuS2 README](https://github.com/meshroomHub/mrRNbNeuS2#2-install-the-testbed). Check:

```bash
ldd $MESHROOM_LOCAL_PLUGINS_PATH/mrRNbNeuS2/RNb-NeuS2/build/testbed | grep "not found"   # must print nothing
```

## 6. SAM 3 checkpoint

The masks are computed by SAM 3, a gated model: request access on
[facebook/sam3](https://huggingface.co/facebook/sam3), then:

```bash
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf download facebook/sam3 sam3.pt --local-dir /path/to/models
sha256sum /path/to/models/sam3.pt
# 9999e2341ceef5e136daa386eecb55cb414446a00ac2b55eb2dfd2f7c3cf8c9e (3 450 062 241 bytes, tested version)
```

and set `RDS_SAM3_MODEL_PATH` to this file (step 3).

## 7. Check

All the templates must open without `CompatibilityNode`:

```bash
source env.sh
python /path/to/visart-eccv26/scripts/check_templates.py $(find /path/to/visart-eccv26/templates -name '*.mgt')
```

`OK` on each line; a `FAIL … UnknownNodeType` names a node whose plugin is missing. Then run a template, see
[Running a template](TEMPLATES.md#running-a-template).
