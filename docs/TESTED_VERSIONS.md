# Tested versions

November 2026, templates as published, full resolution: all nodes succeed, all PS viewpoints calibrated.

| Machine | GPU | warrior | biface | calathos | gourdan_bone (LINO-UniPS) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Ubuntu 26.04 | Quadro RTX 5000, 16 GB | 5 h 38 | 5 h 16 | 7 h 14 | not run (pre-Ampere GPU) |
| Ubuntu 22.04 | Quadro RTX 6000, 24 GB | 5 h 19 | 6 h 13 | 7 h 33 | not run (pre-Ampere GPU) |
| Rocky Linux 9 | A100 | 3 h 08 | 3 h 53 | 5 h 25 | 2 h 24 |

Peaks: 14-19 GB of GPU memory, 42-44 GB of RAM (workstations).

| Software | Version |
| :-- | :-- |
| Meshroom | develop [`1d22fba2`](https://github.com/alicevision/Meshroom/commit/1d22fba2) with the plugin manager fixes now in [#3279](https://github.com/alicevision/Meshroom/pull/3279) (RTX 6000: `de4b5661`) |
| AliceVision | nightly `92b5846f` (RTX 6000: `76d385c0`) |
| Python | 3.11 |
| mrLedGetter | v1.0.2 (Open3D 0.19 on Rocky Linux 9) |
| mrLINOUniPS | v2.0.4 |
| mrRNbNeuS2 | v1.1.2, RNb-NeuS2 v2.0.3 |
| mrSegmentation | [PR #85](https://github.com/meshroomHub/mrSegmentation/pull/85), `976a63b` |
| SAM 3 | `sam3.pt`, SHA-256 `9999e2341ceef5e1…` |

Not tested: the Uni-MS-PS template of the Gourdan bone and the other alternative templates; the nightly bundle at full
resolution (biface at 1000 px only); the UI, Windows, Blackwell GPUs (RTX 50xx).
