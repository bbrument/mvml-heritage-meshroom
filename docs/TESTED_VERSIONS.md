# Tested versions

## 2026-11-13: full resolution

Templates of `templates/` as published, default settings, NEF images of the dataset (8288 × 5520).

| Machine | GPU | warrior | biface | calathos | gourdan_bone (LINO-UniPS) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Workstation, Ubuntu 26.04 | Quadro RTX 5000, 16 GB | 5 h 38 | 5 h 16 | 7 h 14 | not run ([R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere)) |
| Workstation, Ubuntu 22.04 | Quadro RTX 6000, 24 GB | 5 h 19 | 6 h 13 | 7 h 33 | not run (R5) |
| Cluster, Rocky Linux 9 | A100 | 3 h 08 | 3 h 53 | 5 h 25 | 2 h 24 |

All nodes succeed; all PS viewpoints calibrated (13/13, 12/12, 8/8); textured meshes checked visually.

| Resource | Peak |
| :-- | :-- |
| GPU memory | 14 GB (RTX 5000) to 19 GB (RTX 6000); `DepthMap` takes what it finds (61 GB on the A100) |
| RAM | 42-44 GB on the workstations, 92-115 GB on the cluster |
| Disk, project | 97-145 GB per object |

### Software

| | Version |
| :-- | :-- |
| Meshroom | develop [`1d22fba2`](https://github.com/alicevision/Meshroom/commit/1d22fba2) + [#3256](https://github.com/alicevision/Meshroom/pull/3256)-[#3260](https://github.com/alicevision/Meshroom/pull/3260) (RTX 6000: [`de4b5661`](https://github.com/alicevision/Meshroom/commit/de4b5661) + the same) |
| AliceVision | nightly `92b5846f` (RTX 6000: nightly `76d385c0`) |
| Python | 3.11 |
| mrLedGetter | v1.0.2 (Open3D 0.19 on the cluster, [J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234)) |
| mrLINOUniPS | v2.0.4 |
| mrRNbNeuS2 | v1.1.2, testbed of [RNb-NeuS2 v2.0.3](https://github.com/RobinBruneau/RNb-NeuS2/releases/tag/v2.0.3) |
| mrSegmentation | [PR #85](https://github.com/meshroomHub/mrSegmentation/pull/85), `976a63b` |
| SAM 3 | `sam3.pt`, SHA-256 `9999e2341ceef5e1…` |

With these nightly builds, `FeatureMatching` (2.1 → 2.2) and `StructureFromMotion` (3.3 → 3.4) are upgraded silently
when a template is loaded.

### Not tested

- The Uni-MS-PS template of the Gourdan bone (paper method), the other alternative templates.
- Full resolution with the Meshroom nightly bundle (tested at 1000 px only: biface, all nodes succeed).
- The UI, Windows, Blackwell GPUs (RTX 50xx).

## 2026-11-12: low resolution

`biface_visart-eccv26.mgt` and `warrior_lino_unips.mgt` on 1000 px images: all nodes succeed, 15-35 min, 11-13 GB of
GPU memory. Holes and black textures at this resolution only
([B17](KNOWN_ISSUES.md#b17-ledgetterlights-discards-poses-at-low-resolution),
[R6](KNOWN_ISSUES.md#r6-black-texture-at-low-resolution)).

## Templates

Generated with `scripts/build_templates.py`, Meshroom develop
[`edc4b6a2`](https://github.com/alicevision/Meshroom/commit/edc4b6a2), AliceVision `6f9f58ec` and the plugins of the
official registry at [`266f167`](https://github.com/meshroomHub/pluginRegistry/commit/266f167). The four LED-getter
templates have a `ConvertSfMFormat` node in front of the LED-getter nodes
([B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error)).
