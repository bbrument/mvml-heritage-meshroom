# Tested versions

## 2026-11-12: end-to-end runs at low resolution

Fresh install of the plugins with the plugin manager ([INSTALL.md](INSTALL.md)), then two templates run from the
command line (`meshroom_batch` then `meshroom_compute`, as `scripts/run_template.sh` does) on 1000 px versions of the
images of two objects (all the MV and PS images, converted from the NEF to JPEG). Only change to the templates:
`CameraInit.groupCameraFallback=global`, needed by the converted JPEG only.

### Software

| Software | Version |
| :-- | :-- |
| [Meshroom](https://github.com/alicevision/Meshroom) | develop [`de4b5661`](https://github.com/alicevision/Meshroom/commit/de4b5661) (2026-11-12) with [#3256](https://github.com/alicevision/Meshroom/pull/3256) (`0e2062c6`), [#3257](https://github.com/alicevision/Meshroom/pull/3257) (`b199378f`), [#3258](https://github.com/alicevision/Meshroom/pull/3258) (`1f32914d`), [#3259](https://github.com/alicevision/Meshroom/pull/3259) (`ba3c9892`), [#3260](https://github.com/alicevision/Meshroom/pull/3260) (`1e90ceb6`) merged locally |
| [AliceVision](https://github.com/alicevision/AliceVision) | develop [`6f9f58ec`](https://github.com/alicevision/AliceVision/commit/6f9f58ec) built from source (dependencies `AliceVisionDeps-2026.10.12-rocky9-cuda12.8.0`), or the nightly build of 2026-11-12 (`76d385c0`) |
| Python | 3.11 |
| [mrLedGetter](https://github.com/meshroomHub/mrLedGetter) | v1.0.2 |
| [mrLINOUniPS](https://github.com/meshroomHub/mrLINOUniPS) | v2.0.4 (PyTorch 2.7.1, CUDA 12.8) |
| [mrRNbNeuS2](https://github.com/meshroomHub/mrRNbNeuS2) | v1.1.2, with the testbed of [RNb-NeuS2 v2.0.3](https://github.com/RobinBruneau/RNb-NeuS2/releases/tag/v2.0.3) |
| [mrSegmentation](https://github.com/meshroomHub/mrSegmentation) | head of [PR #85](https://github.com/meshroomHub/mrSegmentation/pull/85), `976a63b` (PyTorch 2.5.1, CUDA 12.4) |
| SAM 3 | `sam3.pt` of [facebook/sam3](https://huggingface.co/facebook/sam3), SHA-256 `9999e2341ceef5e1…` |

### Results

| Machine | GPU | AliceVision | `biface_visart-eccv26.mgt` (LED-getter) | `warrior_lino_unips.mgt` (LINO-UniPS) |
| :-- | :-- | :-- | :-- | :-- |
| Laptop, Ubuntu 22.04 | RTX 3080 Laptop, 16 GB (8.6) | `6f9f58ec`, bindings built against numpy 2 | all 20 nodes succeed, 21 min, 12.6 GB of GPU memory; 4 of 6 poses calibrated ([B17](KNOWN_ISSUES.md#b17-ledgetterlights-discards-poses-at-low-resolution)), mesh with holes; black texture ([R6](KNOWN_ISSUES.md#r6-black-texture-at-low-resolution)) | all 13 nodes succeed, 14 min, 11 GB; clean and detailed mesh; almost black texture (R6) |
| Workstation, Ubuntu 22.04 | Quadro RTX 6000, 24 GB (7.5) | nightly `76d385c0` | all 20 nodes succeed with the [B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error) workaround; 5 of 6 poses; black texture (R6) | fails at `LINOUniPS` ([R5](KNOWN_ISSUES.md#r5-lino-unips-fails-on-gpus-older-than-ampere)) |
| Workstation, Ubuntu 22.04 | same | `6f9f58ec`, bindings built against numpy 1 | all 20 nodes succeed with the B14 workaround; 4 of 6 poses; black texture (R6) | not run (R5 expected) |

On both machines the plugin manager installed the four plugins without error (27 GB), and 8 of the 9 templates opened
without `CompatibilityNode` (the ninth, `gourdan_bone_visart-eccv26.mgt`, needs mrUniMSPS, not installed there).
The holes and the black textures come from the low resolution of the test images (see the linked issues).

### Not tested yet

- Full-resolution runs with these versions (the meshes of the paper were computed earlier, with development versions of
  the plugins).
- The other seven templates: warrior and calathos with LED-getter, biface and calathos with LINO-UniPS, and the three
  Gourdan bone templates, including the Uni-MS-PS one of the paper (mrUniMSPS v2.0.4 is in the registry).
- The UI, Windows, Blackwell GPUs (RTX 50xx).

## Templates

The templates of `templates/` were generated with `scripts/build_templates.py`, Meshroom develop
[`edc4b6a2`](https://github.com/alicevision/Meshroom/commit/edc4b6a2), AliceVision `6f9f58ec` and the plugins of the
official registry at [`266f167`](https://github.com/meshroomHub/pluginRegistry/commit/266f167): mrLedGetter v1.0.2,
mrUniMSPS, mrSDMUniPS and mrLINOUniPS v2.0.3, mrRNbNeuS2 v1.1.2, and mrSegmentation `976a63b`. They open without
`CompatibilityNode` with the v2.0.4 releases of the universal photometric stereo plugins.
