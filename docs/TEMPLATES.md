# Templates

Copy `templates/[object]/` into the extracted `[object]/` folder of the
[dataset](https://doi.org/10.5281/zenodo.23500437):

```text
[object]/
├── MV/                              multi-view images (*.NEF)
├── PS/PS_01/ ...                    one image per light (*.NEF)
├── [object]_visart-eccv26.mgt       method of the paper
└── templates/                       alternatives
```

| Template | Photometric stereo | Output |
| :-- | :-- | :-- |
| `warrior_visart-eccv26.mgt` | LED-getter, lights per viewpoint (hand-held flash) | textured mesh |
| `biface_visart-eccv26.mgt` | LED-getter, one light set for the 12-LED rig | textured mesh |
| `calathos_visart-eccv26.mgt` | LED-getter, one light set for the dome | textured mesh |
| `gourdan_bone_visart-eccv26.mgt` | Uni-MS-PS | mesh (no albedo) |
| `[object]/templates/[object]_lino_unips.mgt` | LINO-UniPS (alternative) | textured mesh |
| `gourdan_bone/templates/gourdan_bone_led_getter.mgt` | LED-getter (alternative) | textured mesh |

## Pipelines

- **LED-getter:** RAW to EXR → SAM 3 masks → structure-from-motion (MV + PS) → dense photogrammetry of MV (proxy) →
  `LedGetterLights` → `LedGetterPS` (normals, albedo) → `RNbNeuS2` → `MeshRemoveUnseenFaces` → `Texturing` with the
  albedo. *Light Rig* (on) shares one light set between viewpoints lit by the same LEDs.
- **Uni-MS-PS (Gourdan bone):** only the 23 all-LED images (`all_leds`) for the masks and the SfM, poses copied to the
  other images of each folder → `UniMSPS` on 10 of the 35 lights → `RNbNeuS2`.
- **LINO-UniPS:** masks and SfM as above, no dense photogrammetry → `LINOUniPS` on 10 lights → `RNbNeuS2` →
  `Texturing`.

Masks: SAM 3 with one text prompt per object (`sculpture`, `stone`, `terracotta`, `bone`).

## Settings

Templates set for a 16 GB GPU; the paper used an A100:

| Setting | Templates | Paper |
| :-- | :-- | :-- |
| `downscale` (`LedGetterLights`, `LedGetterPS`, `UniMSPS`, `LINOUniPS`) | 2 | 1 |
| `nbImages` (`UniMSPS`, `LINOUniPS`) | 10 | -1 (all) |
| `meshResolution` (`RNbNeuS2`) | 512 | 1024 |

## Running a template

**UI:** *File > Open Template* (or drop the `.mgt` on the window), drop the object folder on the image gallery, save,
compute.

**Command line:**

```bash
scripts/run_template.sh templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
MESHROOM_BUNDLE=/path/to/Meshroom-2026.11.12-1d22fba-linux scripts/run_template.sh …   # nightly bundle
```

2-8 hours per object at full resolution ([tested versions](TESTED_VERSIONS.md)).

## Regenerating the templates

```bash
python scripts/build_templates.py --tree <output folder>                          # the 9 published templates
python scripts/build_templates.py <output folder> biface_ledgetter warrior_lino   # some of them
python scripts/check_templates.py $(find <output folder> -name '*.mgt')          # CompatibilityNode, node versions
```

With the plugins of [TESTED_VERSIONS.md](TESTED_VERSIONS.md#templates), the output equals `templates/` byte for byte.
