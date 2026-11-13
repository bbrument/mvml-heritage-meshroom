# Installation

How to set up Meshroom, AliceVision and the plugins needed by the [templates](TEMPLATES.md), on Linux, from the
command line (November 2026, see the [tested versions](TESTED_VERSIONS.md)). The templates need the **develop** branch
of Meshroom: no Meshroom release can open them yet. There are two ways to get it:

- **A. the Meshroom nightly bundle**: one archive with Meshroom develop, AliceVision and its Python, nothing to build
  or configure. It lacks the fixes of the plugin manager (below): the RNb-NeuS2 testbed is then installed by hand
  (step 3);
- **B. from source**: AliceVision (nightly build or built from source) and a clone of Meshroom develop, with the fixes
  of the plugin manager merged locally.

> [!IMPORTANT]
> The plugin manager of Meshroom develop still lacks five fixes, open as pull requests
> ([#3256](https://github.com/alicevision/Meshroom/pull/3256) to
> [#3260](https://github.com/alicevision/Meshroom/pull/3260)). Without them, `meshroom_plugins install mrRNbNeuS2`
> reports success but does not install the RNb-NeuS2 testbed (step 3). mrSegmentation is not in the official plugin
> registry yet ([mrSegmentation#85](https://github.com/meshroomHub/mrSegmentation/pull/85)): a registry file of this
> repository adds it (step 2). This page will get shorter as these changes are merged.

Contents: [Requirements](#requirements) · [1. Meshroom and AliceVision](#1-meshroom-and-alicevision)
([A. nightly bundle](#a-meshroom-nightly-bundle), [B. from source](#b-from-source)) · [2. Plugins](#2-plugins) ·
[3. RNb-NeuS2 testbed](#3-rnb-neus2-testbed) · [4. SAM 3 checkpoint](#4-sam-3-checkpoint) · [5. Check](#5-check)

## Requirements

| | |
| :-- | :-- |
| OS | Linux x86_64, glibc 2.35 or newer (tested: Ubuntu 22.04 and 26.04); on glibc 2.34 (RHEL and Rocky Linux 9), mrLedGetter needs a workaround ([J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234)) |
| GPU | NVIDIA, 16 GB: the full-resolution runs of the templates peak at 14 GB on a 16 GB GPU (biface) and 19 GB on a 24 GB GPU (warrior); **compute capability 8.0 or newer for LINO-UniPS** ([R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere)); driver supporting CUDA 12 (570 or newer for RTX 50xx) |
| Disk | about 30 GB for the plugins (26-27 GB for the four plugins of the tested runs) and 3.5 GB for the SAM 3 checkpoint. Per object: 17 to 39 GB of images (extracted from Zenodo), and about **125 GB** for a full-resolution project (measured on the biface) |
| Tools | `git`, [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (way B; the bundle ships its own), a [Hugging Face](https://huggingface.co) account |
| System libraries | `libusb-1.0` (Open3D, [B15](KNOWN_ISSUES.md#other-issues)); for the UI: `libOpenGL`, `libEGL`, `libxcb-cursor` |

## 1. Meshroom and AliceVision

Both ways need the vocabulary tree and the detection models of AliceVision, missing from the nightly builds and from
source installs ([B13](KNOWN_ISSUES.md#other-issues)): `vlfeat_K80L3.SIFT.tree` (ImageMatching fails beyond 200
images without it), `sphereDetection_Mask-RCNN.onnx`, `fcn_resnet50.onnx` and `ColorChartDetectionModel/`. Take them,
for instance, from the `aliceVision/share/aliceVision/` folder of the
[Meshroom 2025.1.0 release](https://github.com/alicevision/Meshroom/releases/tag/v2025.1.0).

### A. Meshroom nightly bundle

Download `Meshroom-<date>-<commit>-linux-full.tar.gz` from the
[Meshroom nightly release](https://github.com/alicevision/Meshroom/releases/tag/nightly) (tested:
`Meshroom-2026.11.12-1d22fba-linux-full.tar.gz`, Meshroom develop `1d22fba2`, AliceVision `92b5846f`) and extract
it. Copy the files of B13 into `<bundle>/aliceVision/share/aliceVision/`: the bundle finds them there.

The commands of the bundle (`meshroom_plugins`, `meshroom_batch`, `meshroom_compute`, and `Meshroom` for the UI) set
their environment themselves: no `env.sh` is needed. The plugins go to `<bundle>/plugins`, or to
`MESHROOM_LOCAL_PLUGINS_PATH` if set. Below, `$M` is the bundle folder:

```bash
M=/path/to/Meshroom-2026.11.12-1d22fba-linux
export RDS_SAM3_MODEL_PATH=/path/to/sam3.pt   # step 4
P=$M/plugins                                  # or $MESHROOM_LOCAL_PLUGINS_PATH
```

Then go to [step 2](#2-plugins) and use `$M/meshroom_plugins` and `$M/bin/uv` there.

### B. From source

**AliceVision.** Either take the nightly build, or build it from source.

- *Nightly build.* Download `AliceVision-nightly-<date>-<commit>-linux.tar.gz` (and `qtAliceVision-nightly-…` for
  the UI) from the [AliceVision nightly release](https://github.com/alicevision/AliceVision/releases/tag/nightly),
  extract them, and copy the files of B13 into `share/aliceVision/`. Nightly builds older than `92b5846f`
  (2026-11-12) also lack the USD resources (`lib64/usd/**/plugInfo.json`): every `.usda` export stops with
  `Failed to find the plugInfo.json file that declares the plugin for ArDefaultResolver`
  ([B9](KNOWN_ISSUES.md#other-issues)); take a newer one.
- *From source.* Follow the [AliceVision build instructions](https://github.com/alicevision/AliceVision/blob/develop/INSTALL.md)
  on the develop branch (tested: [`6f9f58ec`](https://github.com/alicevision/AliceVision/commit/6f9f58ec)). The
  LED-getter templates work with Python bindings (`pyalicevision`) built against numpy 1 or numpy 2
  ([B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error)).

**Meshroom.** Clone the develop branch and merge the five open pull requests of the plugin manager (they merge without
conflict on develop of 2026-11-12, `de4b5661` and `1d22fba2`):

```bash
git clone https://github.com/alicevision/Meshroom.git
cd Meshroom
git checkout -b visart develop
for n in 3256 3257 3258 3259 3260; do
    git fetch origin pull/$n/head:pr$n && git merge --no-ff --no-edit pr$n
done
```

Create the Python environment of Meshroom with the Python of AliceVision (3.11; the nightly build ships it as
`python/bin/python3.11`):

```bash
/path/to/AliceVision/python/bin/python3.11 -m venv ../meshroom-venv
../meshroom-venv/bin/pip install -r requirements.txt -r dev_requirements.txt
```

The plugins build their own environments with `uv` and the Python that runs Meshroom: keep the same Python for all.

**Environment.** Save this as `env.sh`, adapt the paths, and source it before any Meshroom command:

```bash
AV=/path/to/AliceVision                   # nightly build or install folder
MR=/path/to/Meshroom                      # clone above
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
export RDS_SAM3_MODEL_PATH=/path/to/sam3.pt   # step 4
P=$MESHROOM_LOCAL_PLUGINS_PATH
```

For the UI, add `export QML2_IMPORT_PATH=<qtAliceVision>/qml QT_PLUGIN_PATH=<qtAliceVision>` and run
`python $MR/meshroom/ui`. Below, `meshroom_plugins` stands for `python $MR/bin/meshroom_plugins`, and `uv` for the
`uv` of your system.

## 2. Plugins

| Plugin | Needed by | Version tested |
| :-- | :-- | :-- |
| [mrLedGetter](https://github.com/meshroomHub/mrLedGetter) | `[object]_visart-eccv26.mgt` of warrior, biface, calathos; `gourdan_bone_led_getter.mgt` | v1.0.2 |
| [mrLINOUniPS](https://github.com/meshroomHub/mrLINOUniPS) | `[object]_lino_unips.mgt` | v2.0.4 |
| [mrUniMSPS](https://github.com/meshroomHub/mrUniMSPS) | `gourdan_bone_visart-eccv26.mgt` | v2.0.4 (not run end to end, see [tested versions](TESTED_VERSIONS.md)) |
| [mrRNbNeuS2](https://github.com/meshroomHub/mrRNbNeuS2) | all templates | v1.1.2 |
| [mrSegmentation](https://github.com/meshroomHub/mrSegmentation) | all templates (SAM 3 masks) | head of PR #85, `976a63b` |

Install them with the plugin manager, from the command line (`-f` answers its questions; without it, it fails with
`EOFError` when there is no terminal) or from *Manage Plugins* in the UI (with the bundle: `$M/meshroom_plugins`
instead of `meshroom_plugins`):

```bash
meshroom_plugins list            # first call: creates the plugin folder $P
# mrSegmentation is not in the official registry yet: add the registry file of this repository
cp /path/to/visart-eccv26/registry/visartSegmentation.json $P/
for p in mrLedGetter mrLINOUniPS mrUniMSPS mrRNbNeuS2 mrSegmentation; do
    meshroom_plugins install -f $p
done
```

Expect about one hour for mrSegmentation and 5-20 minutes for each of the others (PyTorch and JAX wheels), more if
`uv` cannot reuse its cache (the `uv` of the bundle does not read the cache of older `uv` versions). On glibc 2.34,
mrLedGetter fails to install: see [J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234).

Then fix the environment of mrSegmentation, which does not declare OpenImageIO
([R4](KNOWN_ISSUES.md#r4-mrsegmentation-no-module-named-openimageio)). The bounds keep numpy 1, needed by the
AliceVision bindings; redo it after any `update` of the plugin (with the bundle: `$M/bin/uv` instead of `uv`):

```bash
uv pip install --python $P/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
```

## 3. RNb-NeuS2 testbed

With the pull requests merged (way B), the plugin manager downloads and extracts the compiled RNb-NeuS2 testbed with
mrRNbNeuS2. **Without them (way A, the nightly bundle), `install -f mrRNbNeuS2` ends with `installed` but without the
testbed** ([N1](KNOWN_ISSUES.md#other-issues)); the only trace is a warning `Invalid entry in 'assets'`. Then extract
the archive of the [RNb-NeuS2 v2.0.3 release](https://github.com/RobinBruneau/RNb-NeuS2/releases/tag/v2.0.3) into the
plugin folder by hand, as described in the
[mrRNbNeuS2 README](https://github.com/meshroomHub/mrRNbNeuS2#2-install-the-testbed):

```bash
cd $P/mrRNbNeuS2
wget https://github.com/RobinBruneau/RNb-NeuS2/releases/download/v2.0.3/RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
sha256sum RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
# e0a305c21e1cf7945ac1170322de1873ba179d6128b5a1a186bbf0887c770c42
tar xzf RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz && rm RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
```

In both cases, check:

```bash
ldd $P/mrRNbNeuS2/RNb-NeuS2/build/testbed | grep "not found"   # must print nothing
```

## 4. SAM 3 checkpoint

The masks are computed by SAM 3, a gated model: request access on
[facebook/sam3](https://huggingface.co/facebook/sam3), then:

```bash
uvx --from huggingface_hub hf auth login
uvx --from huggingface_hub hf download facebook/sam3 sam3.pt --local-dir /path/to/models
sha256sum /path/to/models/sam3.pt
# 9999e2341ceef5e136daa386eecb55cb414446a00ac2b55eb2dfd2f7c3cf8c9e (3 450 062 241 bytes, tested version)
```

and set `RDS_SAM3_MODEL_PATH` to this file (step 1).

## 5. Check

All the templates must open without `CompatibilityNode`. From source (way B, `env.sh` sourced):

```bash
python /path/to/visart-eccv26/scripts/check_templates.py $(find /path/to/visart-eccv26/templates -name '*.mgt')
```

With the nightly bundle (way A), the bundle has no `python` command that imports Meshroom: run the script with the
Python of the bundle and these three variables:

```bash
env MESHROOM_INSTALL_DIR=$M LD_LIBRARY_PATH=$M/aliceVision/lib64 PYTHONPATH=$M/lib:$M/aliceVision/lib64/python \
    $M/python/bin/python3.11 /path/to/visart-eccv26/scripts/check_templates.py \
    $(find /path/to/visart-eccv26/templates -name '*.mgt')
```

`OK` on each line; a `FAIL` names a node whose plugin is missing (e.g. `UniMSPS_1 (UniMSPS DescOnlyNodeType)` without
mrUniMSPS). With the bundle, a message
`No module named 'chunk'` about `SDMatte.py` is expected and harmless ([J5](KNOWN_ISSUES.md#other-issues)). Then run
a template, see [Running a template](TEMPLATES.md#running-a-template).
