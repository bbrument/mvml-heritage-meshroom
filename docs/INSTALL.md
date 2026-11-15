# Installation

Linux x86_64, glibc ≥ 2.35, NVIDIA GPU with 16 GB, 64 GB of RAM. Versions: [TESTED_VERSIONS.md](TESTED_VERSIONS.md).
Problems: [Troubleshooting](#troubleshooting).

| Disk | |
| :-- | :-- |
| Meshroom and plugins | 30 GB |
| SAM 3 checkpoint | 3.5 GB |
| One object, full resolution | 17-39 GB of images + 97-145 GB of project |

The templates need Meshroom **develop**. Two ways:

| | [A. Nightly bundle](#1a-nightly-bundle) | [B. From source](#1b-from-source) |
| :-- | :-- | :-- |
| What | one archive: Meshroom, AliceVision, Python | AliceVision nightly + Meshroom clone + 5 open fixes of the plugin manager |
| Environment | none | `scripts/env_source.sh` |
| RNb-NeuS2 testbed | by hand (step 2) | installed with the plugin |
| Tested | 1000 px | full resolution |

```bash
git clone https://github.com/bbrument/visart-eccv26.git
R=$PWD/visart-eccv26
```

## 1a. Nightly bundle

```bash
wget https://github.com/alicevision/Meshroom/releases/download/nightly/Meshroom-2026.11.12-1d22fba-linux-full.tar.gz
tar xzf Meshroom-2026.11.12-1d22fba-linux-full.tar.gz
M=$PWD/Meshroom-2026.11.12-1d22fba-linux
AV=$M/aliceVision
# commands used in the next steps
MP=$M/meshroom_plugins; P=$M/plugins; UV=$M/bin/uv
PY="env MESHROOM_INSTALL_DIR=$M LD_LIBRARY_PATH=$AV/lib64 PYTHONPATH=$M/lib:$AV/lib64/python $M/python/bin/python3.11"
```

## 1b. From source

```bash
wget https://github.com/alicevision/AliceVision/releases/download/nightly/AliceVision-nightly-20261112-92b5846f-linux.tar.gz
tar xzf AliceVision-nightly-20261112-92b5846f-linux.tar.gz
git clone https://github.com/alicevision/Meshroom.git && cd Meshroom
for n in 3256 3257 3258 3259 3260; do git fetch origin pull/$n/head:pr$n && git merge --no-edit pr$n; done
/path/to/AliceVision/python/bin/python3.11 -m venv ../meshroom-venv
../meshroom-venv/bin/pip install -r requirements.txt -r dev_requirements.txt
```

Edit the paths of [`scripts/env_source.sh`](../scripts/env_source.sh), then:

```bash
source $R/scripts/env_source.sh
# commands used in the next steps
MP="python $MR/bin/meshroom_plugins"; P=$MESHROOM_LOCAL_PLUGINS_PATH; UV=uv; PY=python
```

## 2. AliceVision resources and plugins

Vocabulary tree and models, missing from the nightly builds ([B13](KNOWN_ISSUES.md#other-issues)):

```bash
cd $AV/share/aliceVision
G=https://gitlab.com/alicevision
curl -fLO $G/trainedVocabularyTreeData/raw/master/vlfeat_K80L3.SIFT.tree
curl -fLO $G/sphereDetectionModel/-/raw/main/sphereDetection_Mask-RCNN.onnx
curl -fLO $G/semanticSegmentationModel/-/raw/main/fcn_resnet50.onnx
mkdir -p ColorChartDetectionModel
for f in frozen_inference_graph.pb graph.pbtxt; do
    curl -fL -o ColorChartDetectionModel/$f $G/colorChartDetectionModel/-/raw/main/$f
done
```

Plugins, about 1-2 hours:

```bash
$MP list                                         # creates the plugin folder $P
cp $R/registry/visartSegmentation.json $P/       # mrSegmentation, not in the official registry yet
for p in mrLedGetter mrLINOUniPS mrUniMSPS mrRNbNeuS2 mrSegmentation; do $MP install -f $p; done
# mrSegmentation misses OpenImageIO (R4)
$UV pip install --python $P/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
```

**Bundle only:** the RNb-NeuS2 testbed is not downloaded ([N1](KNOWN_ISSUES.md#other-issues)):

```bash
cd $P/mrRNbNeuS2
wget https://github.com/RobinBruneau/RNb-NeuS2/releases/download/v2.0.3/RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
tar xzf RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
```

## 3. SAM 3

Request access on [facebook/sam3](https://huggingface.co/facebook/sam3), then:

```bash
$UV tool run --from huggingface_hub hf auth login
$UV tool run --from huggingface_hub hf download facebook/sam3 sam3.pt --local-dir $HOME/models
export RDS_SAM3_MODEL_PATH=$HOME/models/sam3.pt
```

## 4. Check and run

```bash
$PY $R/scripts/check_templates.py $(find $R/templates -name '*.mgt')     # OK on each line
```

```bash
$R/scripts/run_template.sh $R/templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
# bundle: MESHROOM_BUNDLE=$M $R/scripts/run_template.sh …
```

More: [TEMPLATES.md](TEMPLATES.md#running-a-template).

## Troubleshooting

| Problem | Fix |
| :-- | :-- |
| mrLedGetter install fails on glibc 2.34 (RHEL, Rocky 9) | [J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234) |
| `LINOUniPS` fails on a GPU older than Ampere | none, [R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere) |
| `EOFError` from `meshroom_plugins` | add `-f` |
| `No module named 'chunk'` (SDMatte, bundle) | harmless, [J5](KNOWN_ISSUES.md#other-issues) |
| Open3D: `libusb-1.0.so.0` not found | `sudo apt install libusb-1.0-0` |
| SLURM job killed (out of memory) | reserve the node's RAM: the nodes size themselves on the machine, not on the job (64 GB killed, 240 GB OK) |
| `Failed to find the plugInfo.json …` | AliceVision nightly older than `92b5846f` |

More: [KNOWN_ISSUES.md](KNOWN_ISSUES.md).
