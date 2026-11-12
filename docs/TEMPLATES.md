# Templates

Meshroom pipeline templates (`.mgt`) for the four objects of the
[VISART dataset](https://doi.org/10.5281/zenodo.23500437). `templates/` has the same tree as the dataset: copy each
`templates/[object]/` into the extracted `[object]/` folder, next to `MV/` and `PS/`.

```text
[object]/
├── MV/                              multi-view images (*.NEF), from the dataset
├── PS/PS_01/ ...                    one image per illumination (*.NEF), from the dataset
├── [object]_visart-eccv26.mgt       method of the paper
└── templates/                       alternative methods
```

## Templates

**`[object]_visart-eccv26.mgt` reproduces the method of the paper** for this object:

| Object | Photometric stereo in the paper | Template |
| :-- | :-- | :-- |
| Warrior | LED-getter, self-calibrated near-light, lights calibrated per viewpoint (hand-held flash) | `warrior/warrior_visart-eccv26.mgt` |
| Biface | LED-getter, one set of lights for the 12-LED rig | `biface/biface_visart-eccv26.mgt` |
| Calathos | LED-getter, one set of lights for the RTI dome | `calathos/calathos_visart-eccv26.mgt` |
| Gourdan bone | Uni-MS-PS, universal photometric stereo | `gourdan_bone/gourdan_bone_visart-eccv26.mgt` |

**Alternative templates** (`[object]/templates/`), not the ones of the paper:

| Template | Method | Output |
| :-- | :-- | :-- |
| `[object]/templates/[object]_lino_unips.mgt` (all objects) | LINO-UniPS: normals from its normal network, albedo from its PBR network | RNb-NeuS2 mesh textured with the albedo |
| `gourdan_bone/templates/gourdan_bone_led_getter.mgt` | LED-getter, one set of lights for the dome; proxy from the photogrammetry of the 23 all-LED images | RNb-NeuS2 mesh textured with the albedo |

The dataset provides no masks: every template computes them with SAM 3 (`ImageSegmentationSam3`, plugin
mrSegmentation), with a text prompt per object (`sculpture`, `stone`, `terracotta`, `bone`).

## Pipelines

**Warrior, biface, calathos (LED-getter).** RAW development to EXR, SAM 3 masks, structure-from-motion on all the
images (MV and PS), dense photogrammetry on the MV images (the geometric proxy of LED-getter), export of the
single-light PS images as linear EXR, light calibration (`LedGetterLights`), normals and albedo of each viewpoint
(`LedGetterPS`), RNb-NeuS2 integration of the normals and the albedo, then texturing of the mesh (`Texturing`) with the
albedo maps exported by RNb-NeuS2, brought to a common scale across the viewpoints. The faces seen by no viewpoint
(e.g. the back of the calathos plaque, closed by RNb-NeuS2) are removed beforehand (`MeshRemoveUnseenFaces`).

The LEDs of the biface rig and of the RTI dome are fixed to the camera: `LedGetterLights` calibrates one set of lights
for all the viewpoints lit by the same sequence of LEDs (option *Light Rig*). For the calathos, the six viewpoints of
35 dome LEDs share one set of lights; `PS_07` (105 LEDs) and `PS_08` (hand-held flash) are calibrated alone. Disable
*Light Rig* to calibrate every viewpoint independently.

**Gourdan bone (Uni-MS-PS).** The bone has no separate multi-view set: the template works on its 23 viewpoints only.
Only the 23 all-LED images (file name containing `all_leds`) are masked and used for structure-from-motion; their poses
are then transferred to the other images of their folder. The photometric stereo node finds the all-LED image of each
viewpoint by its file name (*Pose Reference Pattern* = `all_leds`) and uses a fixed random subset of 10 of the 35
single-LED images, with the mask of the all-LED image. RNb-NeuS2 integrates the normals (Uni-MS-PS estimates no albedo,
so this mesh is not textured).

**LINO-UniPS (alternative).** Masks and structure-from-motion as above (all the images for warrior, biface and
calathos; the all-LED images for the Gourdan bone), without dense photogrammetry, then LINO-UniPS normals and albedo on
10 lighting images per viewpoint, RNb-NeuS2 and texturing with the albedo.

## Settings: workstation and paper

The meshes of the paper were computed on NVIDIA A100 GPUs, with full-resolution normal maps and an RNb-NeuS2
marching-cubes resolution of 1024. On a 16 GB GPU, full-resolution photometric stereo can run out of memory (its memory
also grows with the number of lighting images per pose) and the 1024 marching cubes do not fit. The templates are set
for a workstation:

| Setting | Templates (workstation) | Paper (A100) |
| :-- | :-- | :-- |
| `downscale` of the photometric stereo nodes (`LedGetterLights`, `LedGetterPS`, `UniMSPS`, `LINOUniPS`) | 2 | 1 (full resolution) |
| `nbImages` of the universal photometric stereo nodes (`UniMSPS`, `LINOUniPS`) | 10 (random subset, fixed seed) | -1 (all images) |
| `meshResolution` of `RNbNeuS2` | 512 | 1024 |

LED-getter always uses all the lighting images of a viewpoint.

## Running a template

**In the UI.** Open the template with *Open Template* in the *File* menu, or drag and drop the `.mgt` file on the
window (*File > Open* lists only `.mg` files), then drop the object folder on the image gallery, save the project and compute. To list the templates in
*File > New*, add the folder that holds them to `MESHROOM_PIPELINE_TEMPLATES_PATH`.

**From the command line.** `scripts/run_template.sh` creates the project with `meshroom_batch` and computes it with
`meshroom_compute` (environment of [INSTALL.md](INSTALL.md) sourced):

```bash
scripts/run_template.sh templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
```

It passes the image folders as one value (`meshroom_batch -i` keeps only the last of several values, see
[R3](KNOWN_ISSUES.md#r3-meshroom_batch--i-keeps-only-the-last-folder)). Add `CONVERT_SFM=1` for an AliceVision whose
Python bindings are built against numpy 1, such as the nightly bundle
([B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error)).

Expect several hours per object at full resolution on a workstation GPU. The runs of
[TESTED_VERSIONS.md](TESTED_VERSIONS.md) were made on 1000 px versions of the images (15-35 min).

## Regenerating the templates

`scripts/build_templates.py` builds all the templates from Python. With Meshroom and the plugins of the tested versions
on the Python path:

```bash
python scripts/build_templates.py --tree <output folder>      # the 9 published templates, tree of templates/
python scripts/build_templates.py <output folder> biface_ledgetter warrior_lino
```

With the plugin versions of the [tested versions](TESTED_VERSIONS.md#templates), the output is identical, byte for
byte, to the files of `templates/`. The node versions written in a template follow the installed plugins: compare
with `templates/` before replacing them. `scripts/check_templates.py` checks that templates open without
`CompatibilityNode` and lists the node versions that differ from the installed ones.
