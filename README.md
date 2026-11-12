<img src="assets/banner.png" width="100%" alt="Textured reconstructions of the four objects of the VISART dataset: warrior head, flint biface, woman with a calathos and Gourdan bone">

<!-- TODO at the Zenodo publication: check the dataset DOI (version DOI 10.5281/zenodo.23500437, concept DOI known
only then), add the paper DOI to the badges and the BibTeX, update CITATION.cff. -->

# Integrating Multi-view Multi-light Surface Reconstruction into Cultural Heritage Workflows

[![ECCV 2026 Workshops](https://img.shields.io/badge/ECCV%202026-VISART%20workshop-red)](#citation)
[![Dataset DOI](https://img.shields.io/badge/dataset-10.5281%2Fzenodo.23500437-blue)](https://doi.org/10.5281/zenodo.23500437)
[![Data license: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-yellow)](LICENSE)
[![Meshroom develop](https://img.shields.io/badge/Meshroom-develop-green)](https://github.com/alicevision/Meshroom/tree/develop)

Baptiste Brument<sup>1</sup> · Robin Bruneau<sup>2</sup> · Benjamin Coupry<sup>1</sup> · Vincent Demoulin<sup>3</sup> ·
Jean Mélou<sup>4</sup> · Antoine Laurent<sup>5</sup> · Fabien Castan<sup>3</sup> · Jean-Denis Durou<sup>1</sup> ·
Lilian Calvet<sup>6</sup>

<sup>1</sup> IRIT, UMR 5505, CNRS, Toulouse · <sup>2</sup> University of Zurich · <sup>3</sup> The Mill ·
<sup>4</sup> Fittingbox, Labège · <sup>5</sup> TRACES, UMR 5608, CNRS, Toulouse ·
<sup>6</sup> ROCS, Balgrist University Hospital, University of Zurich

**Companion repository of the VISART dataset**: Meshroom templates, installation guide and tested versions to
reconstruct the four archaeological objects of the paper from their raw multi-view and multi-light images. The images
are on [Zenodo](https://doi.org/10.5281/zenodo.23500437); this repository holds everything that changes with the
software: versions, installation, settings, known issues.

## Updates

- **2026-11-12**: first version. Templates in the `.mgt` format of Meshroom develop; end-to-end runs at low resolution
  with the plugins installed by the Meshroom plugin manager ([tested versions](docs/TESTED_VERSIONS.md)).

## The dataset

Four objects, each imaged as a multi-view set (MV, one illumination) and a multi-light set (PS, several viewpoints each
under several illuminations), as Nikon RAW files (NEF, 45.7 MP).

| Object | MV images | PS viewpoints × lights | PS images | Method of the paper | Template |
| :-- | --: | :-- | --: | :-- | :-- |
| Warrior | 121 | 13 × 8-10 (hand-held flash) | 114 | LED-getter | [`warrior_visart-eccv26.mgt`](templates/warrior/warrior_visart-eccv26.mgt) |
| Biface | 162 | 12 × 13 (12-LED rig) | 156 | LED-getter | [`biface_visart-eccv26.mgt`](templates/biface/biface_visart-eccv26.mgt) |
| Calathos | 48 | 6 × 36, 1 × 106, 1 × 29 (RTI dome, flash) | 351 | LED-getter | [`calathos_visart-eccv26.mgt`](templates/calathos/calathos_visart-eccv26.mgt) |
| Gourdan bone | (in PS) | 23 × 36 (RTI dome) | 828 | Uni-MS-PS | [`gourdan_bone_visart-eccv26.mgt`](templates/gourdan_bone/gourdan_bone_visart-eccv26.mgt) |

Acquisition, file naming and object descriptions: see the [dataset page](https://doi.org/10.5281/zenodo.23500437).
The dataset provides no masks: the templates compute them with SAM 3.

## Quick start

1. Download `[object]_MV.zip` and `[object]_PS.zip` from [Zenodo](https://doi.org/10.5281/zenodo.23500437) and extract
   them in the same folder.
2. Install Meshroom develop, AliceVision and the plugins: [docs/INSTALL.md](docs/INSTALL.md).
3. Copy `templates/[object]/` of this repository into the extracted `[object]/` folder.
4. Open the template in Meshroom (*Open Template*), drop the object folder on the image gallery and compute, or, from
   the command line:

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

`[object]_visart-eccv26.mgt` reproduces the method of the paper; `templates/` holds alternatives (LINO-UniPS for all
objects, LED-getter for the Gourdan bone). Each pipeline goes from the RAW images to a mesh textured with the albedo:
SAM 3 masks, structure-from-motion, photometric stereo per viewpoint, RNb-NeuS2 integration of the normals and albedo,
texturing. Details, and how to regenerate the templates with `scripts/build_templates.py`:
[docs/TEMPLATES.md](docs/TEMPLATES.md).

The templates are set for a 16 GB GPU. To reproduce the settings of the paper (NVIDIA A100):

| Setting | Templates | Paper |
| :-- | :-- | :-- |
| `downscale` of the photometric stereo nodes | 2 | 1 |
| `nbImages` of `UniMSPS` and `LINOUniPS` | 10 | -1 (all) |
| `meshResolution` of `RNbNeuS2` | 512 | 1024 |

## Installation

The templates need Meshroom **develop**. In short ([full guide](docs/INSTALL.md)):

- AliceVision develop, built from source or nightly build, plus a few missing resources;
- Meshroom develop, with five open fixes of the plugin manager merged locally
  ([#3256](https://github.com/alicevision/Meshroom/pull/3256)-[#3260](https://github.com/alicevision/Meshroom/pull/3260));
- the plugins, with `meshroom_plugins install`: mrLedGetter, mrUniMSPS, mrLINOUniPS, mrRNbNeuS2 from the official
  registry, mrSegmentation through [`registry/visartSegmentation.json`](registry/visartSegmentation.json);
- the SAM 3 checkpoint, from Hugging Face (gated model).

## Tested versions and known issues

Last end-to-end test: **2026-11-12**, Meshroom develop `de4b5661` with the five fixes, AliceVision `6f9f58ec` or nightly,
mrLedGetter v1.0.2, mrLINOUniPS v2.0.4, mrRNbNeuS2 v1.1.2, mrSegmentation `976a63b`, at low resolution, on two of the
nine templates ([details](docs/TESTED_VERSIONS.md)).

Main limitations ([all issues and workarounds](docs/KNOWN_ISSUES.md)):

- LINO-UniPS needs a GPU of compute capability 8.0 or newer (Ampere).
- mrSegmentation is not in the official registry yet, and misses a dependency (OpenImageIO).
- With the nightly build of AliceVision, the LED-getter nodes need an extra `ConvertSfMFormat` node
  (`scripts/add_convert_sfm.py`).
- At low resolution (1000 px test images), LED-getter discards poses and the textures come out black: use the
  full-resolution images.

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
  note      = {DOI forthcoming}
}
```
