# Installation

Linux x86_64 (glibc ≥ 2.35), NVIDIA GPU with 16 GB (Ampere or newer for the LINO-UniPS templates), 64 GB of RAM.
Disk: 30 GB for Meshroom and the plugins, 3.5 GB for SAM 3; per object, 17-39 GB of images and 97-145 GB of project.

## 1. Meshroom develop (nightly bundle)

Latest bundle: [Meshroom nightly release](https://github.com/alicevision/Meshroom/releases/tag/nightly) (tested:
`2026.11.12-1d22fba`).

```bash
git clone https://github.com/bbrument/mvml-heritage-meshroom.git && R=$PWD/mvml-heritage-meshroom
# download Meshroom-<date>-<commit>-linux-full.tar.gz from the nightly release above
tar xzf Meshroom-*-linux-full.tar.gz
M=$(ls -d $PWD/Meshroom-*-linux); AV=$M/aliceVision; MP=$M/meshroom_plugins; P=$M/plugins
```

From source instead: [Meshroom](https://github.com/alicevision/Meshroom) develop with
[#3279](https://github.com/alicevision/Meshroom/pull/3279) merged and the
[AliceVision nightly](https://github.com/alicevision/AliceVision/releases/tag/nightly), then steps 2-5 with the
`meshroom_plugins` of the clone.

## 2. Vocabulary tree

Missing from the nightly builds:

```bash
curl -fL -o $AV/share/aliceVision/vlfeat_K80L3.SIFT.tree \
    https://gitlab.com/alicevision/trainedVocabularyTreeData/raw/master/vlfeat_K80L3.SIFT.tree
```

## 3. Plugins

About 1-2 hours:

```bash
$MP list                                         # creates the plugin folder $P
cp $R/registry/visartSegmentation.json $P/       # mrSegmentation, not in the official registry yet
for p in mrLedGetter mrLINOUniPS mrUniMSPS mrRNbNeuS2 mrSegmentation; do $MP install -f $p; done
# mrSegmentation (PR #85) does not declare OpenImageIO; redo after any update of the plugin
$M/bin/uv pip install --python $P/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
# the bundle does not download the RNb-NeuS2 testbed
cd $P/mrRNbNeuS2
wget https://github.com/RobinBruneau/RNb-NeuS2/releases/download/v2.0.3/RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
tar xzf RNb-NeuS2-2.0.3-linux-x86_64-cu128.tar.gz
```

## 4. SAM 3

Request access on [facebook/sam3](https://huggingface.co/facebook/sam3), then:

```bash
$M/bin/uv tool run --from huggingface_hub hf auth login
$M/bin/uv tool run --from huggingface_hub hf download facebook/sam3 sam3.pt --local-dir $HOME/models
export RDS_SAM3_MODEL_PATH=$HOME/models/sam3.pt
```

## 5. Check

`OK` on each line:

```bash
env MESHROOM_INSTALL_DIR=$M LD_LIBRARY_PATH=$AV/lib64 PYTHONPATH=$M/lib:$AV/lib64/python \
    $M/python/bin/python3.11 $R/scripts/check_templates.py $(find $R/templates -name '*.mgt')
```

Then run a template: [Quick start](../README.md#quick-start).

## Troubleshooting

| Problem | Fix |
| :-- | :-- |
| `LINOUniPS`: `expected scalar type Half but found BFloat16` | GPU older than Ampere: use the other templates |
| Open3D: `libusb-1.0.so.0` not found | `sudo apt install libusb-1.0-0` |
| `No module named 'chunk'` (SDMatte) at each command | harmless |
