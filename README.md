<img src="assets/banner.png" width="100%" alt="Textured reconstructions of the four objects of the VISART dataset: warrior head, flint biface, woman with a calathos and Gourdan bone">

<!-- TODO at the Zenodo publication: check the dataset DOI (version DOI 10.5281/zenodo.23500437, concept DOI known
only then); proceedings DOI of the paper when available (badges, BibTeX, CITATION.cff). -->

# Integrating Multi-view Multi-light Surface Reconstruction into Cultural Heritage Workflows

[![ECCV 2026 Workshops](https://img.shields.io/badge/ECCV%202026-VISART%20workshop-red)](#citation)
[![arXiv](https://img.shields.io/badge/arXiv-2609.15833-b31b1b)](https://arxiv.org/abs/2609.15833)
[![Dataset DOI](https://img.shields.io/badge/dataset-10.5281%2Fzenodo.23500437-blue)](https://doi.org/10.5281/zenodo.23500437)
[![Data license: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-yellow)](LICENSE)
[![Meshroom develop](https://img.shields.io/badge/Meshroom-develop-green)](https://github.com/alicevision/Meshroom/tree/develop)

[Baptiste Brument](https://bbrument.github.io/) · [Robin Bruneau](https://robinbruneau.github.io/) ·
[Benjamin Coupry](https://scholar.google.com/citations?user=H5LhL7AAAAAJ) · [Vincent Demoulin](https://www.linkedin.com/in/vincent-demoulin-6b9562a9/) ·
[Jean Mélou](https://scholar.google.com/citations?user=t9PRZ3AAAAAJ) ·
[Antoine Laurent](https://cv.hal.science/antoine-laurent-archeologie) ·
[Fabien Castan](https://www.linkedin.com/in/fabien-castan-99729453/) ·
[Jean-Denis Durou](https://cv.hal.science/jean-denis-durou) ·
[Lilian Calvet](https://www.linkedin.com/in/lilian-calvet-42b1a689/)

Meshroom templates that reconstruct the four archaeological objects of the VISART dataset from their raw images
([paper](https://arxiv.org/abs/2609.15833)).

## Data

Images on [Zenodo](https://doi.org/10.5281/zenodo.23500437): `[object]_MV.zip` and `[object]_PS.zip` (Gourdan bone:
PS only), Nikon RAW (NEF, 8288 × 5520), no masks (the templates compute them with SAM 3). File names, cameras and
lighting: [dataset page](https://doi.org/10.5281/zenodo.23500437).

| Object | MV images | PS viewpoints × lights | PS images | Method of the paper |
| :-- | --: | :-- | --: | :-- |
| Warrior | 121 | 13 × 8-10 (hand-held flash) | 114 | LED-getter |
| Biface | 162 | 12 × 13 (12-LED rig) | 156 | LED-getter |
| Calathos | 48 | 6 × 36, 1 × 106, 1 × 29 (RTI dome, flash) | 351 | LED-getter |
| Gourdan bone | (in PS) | 23 × 36 (RTI dome) | 828 | Uni-MS-PS |

## Quick start

1. Install Meshroom develop and the plugins: [docs/INSTALL.md](docs/INSTALL.md).
2. Extract the archives of an object from Zenodo, and copy `templates/[object]/` into the extracted folder:

   ```text
   [object]/
   ├── MV/*.NEF                         multi-view set, one illumination
   ├── PS/PS_xx/*.NEF                   multi-light set: one folder per viewpoint, one image per light
   ├── [object]_visart-eccv26.mgt       method of the paper
   └── templates/                       alternatives
   ```

3. Compute:
   - **UI:** *File > Open Template*, drop the object folder on the image gallery, save, compute.
   - **Command line:**

     ```bash
     scripts/run_template.sh templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
     # nightly bundle: MESHROOM_BUNDLE=/path/to/Meshroom-2026.11.12-1d22fba-linux scripts/run_template.sh …
     ```

2-8 hours per object at full resolution.

## Templates

| Template | Photometric stereo | Output |
| :-- | :-- | :-- |
| `warrior_visart-eccv26.mgt` | LED-getter, lights per viewpoint (hand-held flash) | textured mesh |
| `biface_visart-eccv26.mgt` | LED-getter, one light set for the 12-LED rig | textured mesh |
| `calathos_visart-eccv26.mgt` | LED-getter, one light set for the dome | textured mesh |
| `gourdan_bone_visart-eccv26.mgt` | Uni-MS-PS | mesh (no albedo) |
| `[object]/templates/[object]_lino_unips.mgt` | LINO-UniPS (alternative) | textured mesh |
| `gourdan_bone/templates/gourdan_bone_led_getter.mgt` | LED-getter (alternative) | textured mesh |

- **LED-getter:** RAW to EXR → SAM 3 masks → structure-from-motion (MV + PS) → dense photogrammetry of MV (proxy) →
  `LedGetterLights` → `LedGetterPS` (normals, albedo) → `RNbNeuS2` → `MeshRemoveUnseenFaces` → `Texturing` with the
  albedo.
- **Uni-MS-PS (Gourdan bone):** masks and SfM on the 23 all-LED images, poses copied to the other images of each
  folder → `UniMSPS` on 10 of the 35 lights → `RNbNeuS2`.
- **LINO-UniPS:** masks and SfM as above, no dense photogrammetry → `LINOUniPS` on 10 lights → `RNbNeuS2` →
  `MeshRemoveUnseenFaces` → `Texturing`.

Set for a 16 GB GPU; the paper used an A100:

| Setting | Templates | Paper |
| :-- | :-- | :-- |
| `downscale` (`LedGetterLights`, `LedGetterPS`, `UniMSPS`, `LINOUniPS`) | 2 | 1 |
| `nbImages` (`UniMSPS`, `LINOUniPS`) | 10 | -1 (all) |
| `meshResolution` (`RNbNeuS2`) | 512 | 1024 |

Generated by [`scripts/build_templates.py`](scripts/build_templates.py).

## Tested versions

November 2026, templates as published, full resolution: all nodes succeed, all PS viewpoints calibrated.

| Machine | GPU | warrior | biface | calathos | gourdan_bone (LINO-UniPS) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Ubuntu 26.04 | Quadro RTX 5000, 16 GB | 5 h 38 | 5 h 16 | 7 h 14 | not run (pre-Ampere GPU) |
| Ubuntu 22.04 | Quadro RTX 6000, 24 GB | 5 h 19 | 6 h 13 | 7 h 33 | not run (pre-Ampere GPU) |
| Rocky Linux 9 | A100 | 3 h 08 | 3 h 53 | 5 h 25 | 2 h 24 |

Meshroom develop [`1d22fba2`](https://github.com/alicevision/Meshroom/commit/1d22fba2) with the plugin manager fixes
now in [#3279](https://github.com/alicevision/Meshroom/pull/3279), AliceVision nightly `92b5846f` (RTX 6000: Meshroom
`de4b5661`, AliceVision `76d385c0`), Python 3.11, mrLedGetter v1.0.2 (Open3D 0.19 on Rocky Linux 9), mrLINOUniPS
v2.0.4, mrRNbNeuS2 v1.1.2 (RNb-NeuS2 v2.0.3), mrSegmentation
[PR #85](https://github.com/meshroomHub/mrSegmentation/pull/85) `976a63b`, `sam3.pt` (SHA-256 `9999e2341ceef5e1…`).
Peaks: 14-19 GB of GPU memory, 42-44 GB of RAM (workstations).

Not tested: the Uni-MS-PS template of the Gourdan bone and the other alternative templates; the nightly bundle at full
resolution (biface at 1000 px only); the UI, Windows, Blackwell GPUs (RTX 50xx).

## Related projects

| Repository | Role |
| :-- | :-- |
| [Meshroom](https://github.com/alicevision/Meshroom), [AliceVision](https://github.com/alicevision/AliceVision) | Node-based 3D reconstruction framework, photogrammetry |
| [mrLedGetter](https://github.com/meshroomHub/mrLedGetter) | Self-calibrated near-light photometric stereo (LED-getter) |
| [mrUniMSPS](https://github.com/meshroomHub/mrUniMSPS) | Universal photometric stereo (Uni-MS-PS) |
| [mrLINOUniPS](https://github.com/meshroomHub/mrLINOUniPS) | Universal photometric stereo (LINO-UniPS), normals and albedo |
| [mrRNbNeuS2](https://github.com/meshroomHub/mrRNbNeuS2), [RNb-NeuS2](https://github.com/RobinBruneau/RNb-NeuS2) | Multi-view integration of normals and reflectance |
| [mrSegmentation](https://github.com/meshroomHub/mrSegmentation) | Object masks (SAM 3) |

## License

Code and templates: [MIT](LICENSE). Dataset: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), see
[Zenodo](https://doi.org/10.5281/zenodo.23500437).

## Acknowledgements

Baptiste Brument was funded by the OPEN-DOPAMIn project (CNRS Innovation). This work was granted access to the Juliet
computing platform, supported by a French government grant managed by the Agence Nationale de la Recherche under the
"Investissements d'avenir" program (reference "ANR-21-ESRE-0051"). It has been supported by the University of Zurich
and University Hospital Balgrist. We thank the Musée Saint-Raymond, Toulouse, for access to the warrior head and the
woman with a calathos.

## Citation

If you use the dataset or these templates, please cite:

```bibtex
@inproceedings{brument2026mvps,
  author    = {Brument, Baptiste and Bruneau, Robin and Coupry, Benjamin and Demoulin, Vincent and M{\'e}lou, Jean and Laurent, Antoine and Castan, Fabien and Durou, Jean-Denis and Calvet, Lilian},
  title     = {Integrating Multi-view Multi-light Surface Reconstruction into Cultural Heritage Workflows},
  booktitle = {European Conference on Computer Vision (ECCV) Workshops, VISART},
  year      = {2026},
  eprint    = {2609.15833},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  url       = {https://arxiv.org/abs/2609.15833}
}
```
