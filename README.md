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

**Companion repository of the VISART dataset** ([paper](https://arxiv.org/abs/2609.15833)): Meshroom templates to
reconstruct its four archaeological objects from the raw images, installation guide, tested versions. Images on
[Zenodo](https://doi.org/10.5281/zenodo.23500437).

## The dataset

Four objects, each imaged as a multi-view set (MV, one illumination) and a multi-light set (PS, several viewpoints each
under several illuminations), as Nikon RAW files (NEF, 45.7 MP).

| Object | MV images | PS viewpoints × lights | PS images | Method of the paper | Template |
| :-- | --: | :-- | --: | :-- | :-- |
| Warrior | 121 | 13 × 8-10 (hand-held flash) | 114 | LED-getter | [`warrior_visart-eccv26.mgt`](templates/warrior/warrior_visart-eccv26.mgt) |
| Biface | 162 | 12 × 13 (12-LED rig) | 156 | LED-getter | [`biface_visart-eccv26.mgt`](templates/biface/biface_visart-eccv26.mgt) |
| Calathos | 48 | 6 × 36, 1 × 106, 1 × 29 (RTI dome, flash) | 351 | LED-getter | [`calathos_visart-eccv26.mgt`](templates/calathos/calathos_visart-eccv26.mgt) |
| Gourdan bone | (in PS) | 23 × 36 (RTI dome) | 828 | Uni-MS-PS | [`gourdan_bone_visart-eccv26.mgt`](templates/gourdan_bone/gourdan_bone_visart-eccv26.mgt) |

Details: [dataset page](https://doi.org/10.5281/zenodo.23500437). No masks: the templates compute them with SAM 3.

## Quick start

1. Download and extract `[object]_MV.zip` and `[object]_PS.zip` from [Zenodo](https://doi.org/10.5281/zenodo.23500437).
2. Install Meshroom and the plugins: [docs/INSTALL.md](docs/INSTALL.md).
3. Copy `templates/[object]/` into the extracted `[object]/` folder.
4. Open the template in Meshroom (*Open Template*) and drop the object folder on the gallery, or:

```bash
scripts/run_template.sh templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
```

## Templates

```text
templates/
├── warrior/
│   ├── warrior_visart-eccv26.mgt            method of the paper (LED-getter)
│   └── templates/
│       └── warrior_lino_unips.mgt           alternative (LINO-UniPS)
├── biface/
│   ├── biface_visart-eccv26.mgt             method of the paper (LED-getter)
│   └── templates/
│       └── biface_lino_unips.mgt            alternative (LINO-UniPS)
├── calathos/
│   ├── calathos_visart-eccv26.mgt           method of the paper (LED-getter)
│   └── templates/
│       └── calathos_lino_unips.mgt          alternative (LINO-UniPS)
└── gourdan_bone/
    ├── gourdan_bone_visart-eccv26.mgt       method of the paper (Uni-MS-PS)
    └── templates/
        ├── gourdan_bone_lino_unips.mgt      alternative (LINO-UniPS)
        └── gourdan_bone_led_getter.mgt      alternative (LED-getter)
```

Pipelines, settings of the paper (A100: `downscale` 1, all lights, `meshResolution` 1024) and regeneration:
[docs/TEMPLATES.md](docs/TEMPLATES.md).

## Installation

Meshroom **develop** (nightly bundle), five plugins and the SAM 3 checkpoint, about two hours:
[docs/INSTALL.md](docs/INSTALL.md).

## Tested versions and known issues

Tested in November 2026 at full resolution on three machines: [docs/TESTED_VERSIONS.md](docs/TESTED_VERSIONS.md).
Known issues (LINO-UniPS needs an Ampere or newer GPU; mrSegmentation not yet in the official registry):
[docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md).

## Related projects

| Repository | Role |
| :-- | :-- |
| [Meshroom](https://github.com/alicevision/Meshroom), [AliceVision](https://github.com/alicevision/AliceVision) | Node-based 3D reconstruction framework, photogrammetry |
| [mrLedGetter](https://github.com/meshroomHub/mrLedGetter) | Self-calibrated near-light photometric stereo (LED-getter) |
| [mrUniMSPS](https://github.com/meshroomHub/mrUniMSPS) | Universal photometric stereo (Uni-MS-PS) |
| [mrLINOUniPS](https://github.com/meshroomHub/mrLINOUniPS) | Universal photometric stereo (LINO-UniPS), normals and albedo |
| [mrSDMUniPS](https://github.com/meshroomHub/mrSDMUniPS) | Universal photometric stereo (SDM-UniPS), no template provided |
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

## Updates

- **2026-11-12**: first version. History of the changes and of the tests: [docs/CHANGELOG.md](docs/CHANGELOG.md).
