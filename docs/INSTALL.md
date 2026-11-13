# Installation

Linux x86_64, glibc ≥ 2.35, NVIDIA GPU with 16 GB. Versions: [TESTED_VERSIONS.md](TESTED_VERSIONS.md).
Problems: [Troubleshooting](#troubleshooting).

| Disk | |
| :-- | :-- |
| Meshroom and plugins | 30 GB |
| SAM 3 checkpoint | 3.5 GB |
| One object, full resolution | 17-39 GB of images + about 125 GB of project |

## 1. Meshroom

The templates need Meshroom **develop**: take the nightly bundle (Meshroom, AliceVision, Python).

```bash
git clone https://github.com/bbrument/visart-eccv26.git
R=$PWD/visart-eccv26
wget https://github.com/alicevision/Meshroom/releases/download/nightly/Meshroom-2026.11.12-1d22fba-linux-full.tar.gz
tar xzf Meshroom-2026.11.12-1d22fba-linux-full.tar.gz
M=$PWD/Meshroom-2026.11.12-1d22fba-linux
```

Add the vocabulary tree and the models missing from the bundle ([B13](KNOWN_ISSUES.md#other-issues)):

```bash
cd $M/aliceVision/share/aliceVision           # from source: $AV/share/aliceVision
G=https://gitlab.com/alicevision
curl -fLO $G/trainedVocabularyTreeData/raw/master/vlfeat_K80L3.SIFT.tree
curl -fLO $G/sphereDetectionModel/-/raw/main/sphereDetection_Mask-RCNN.onnx
curl -fLO $G/semanticSegmentationModel/-/raw/main/fcn_resnet50.onnx
mkdir -p ColorChartDetectionModel
for f in frozen_inference_graph.pb graph.pbtxt; do
    curl -fL -o ColorChartDetectionModel/$f $G/colorChartDetectionModel/-/raw/main/$f
done
```

## 2. Plugins

```bash
$M/meshroom_plugins list                                       # creates $M/plugins
cp $R/registry/visartSegmentation.json $M/plugins/               # mrSegmentation, not in the official registry yet
for p in mrLedGetter mrLINOUniPS mrUniMSPS mrRNbNeuS2 mrSegmentation; do
    $M/meshroom_plugins install -f $p
done
```

About 1-2 hours (PyTorch, JAX). Then two fixes:

```bash
# mrSegmentation misses OpenImageIO (R4)
$M/bin/uv pip install --python $M/plugins/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"

# the RNb-NeuS2 testbed is not downloaded by the plugin manager of the bundle (N1)
cd $M/plugins/mrRNbNeuS2
wget https://github.com/RobinBruneau/RNb-NeuS2/releases/download/v2.0.3/RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
tar xzf RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
```

## 3. SAM 3

Request access on [facebook/sam3](https://huggingface.co/facebook/sam3), then:

```bash
$M/bin/uv tool run --from huggingface_hub hf auth login
$M/bin/uv tool run --from huggingface_hub hf download facebook/sam3 sam3.pt --local-dir $HOME/models
export RDS_SAM3_MODEL_PATH=$HOME/models/sam3.pt
```

## 4. Check

```bash
env MESHROOM_INSTALL_DIR=$M LD_LIBRARY_PATH=$M/aliceVision/lib64 PYTHONPATH=$M/lib:$M/aliceVision/lib64/python \
    $M/python/bin/python3.11 $R/scripts/check_templates.py $(find $R/templates -name '*.mgt')
```

Expect `OK` on each line. Then [run a template](TEMPLATES.md#running-a-template):

```bash
MESHROOM_BUNDLE=$M $R/scripts/run_template.sh $R/templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
```

## From source

Instead of the bundle: AliceVision ([nightly](https://github.com/alicevision/AliceVision/releases/tag/nightly) or
[built](https://github.com/alicevision/AliceVision/blob/develop/INSTALL.md)) and Meshroom develop with the five open
fixes of the plugin manager, which also install the RNb-NeuS2 testbed:

```bash
git clone https://github.com/alicevision/Meshroom.git && cd Meshroom
for n in 3256 3257 3258 3259 3260; do git fetch origin pull/$n/head:pr$n && git merge --no-edit pr$n; done
/path/to/AliceVision/python/bin/python3.11 -m venv ../meshroom-venv
../meshroom-venv/bin/pip install -r requirements.txt -r dev_requirements.txt
```

Then edit and source [`scripts/env_source.sh`](../scripts/env_source.sh), and follow steps 1-4 with
`python $MR/bin/meshroom_plugins`, `uv`, `$MESHROOM_LOCAL_PLUGINS_PATH` and `python $R/scripts/check_templates.py`.

## Troubleshooting

| Problem | Fix |
| :-- | :-- |
| mrLedGetter install fails on glibc 2.34 (RHEL, Rocky 9) | [J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234) |
| `LINOUniPS` fails on a GPU older than Ampere | none, [R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere) |
| `EOFError` from `meshroom_plugins` | add `-f` |
| `No module named 'chunk'` (SDMatte) | harmless, [J5](KNOWN_ISSUES.md#other-issues) |
| Open3D: `libusb-1.0.so.0` not found | `sudo apt install libusb-1.0-0` |
| `Failed to find the plugInfo.json …` | AliceVision nightly older than `92b5846f`, [B9](KNOWN_ISSUES.md#other-issues) |

More: [KNOWN_ISSUES.md](KNOWN_ISSUES.md).
