# Known issues

Issues met while installing and running the templates with the [tested versions](TESTED_VERSIONS.md) (November
2026), with their workarounds. The labels (R*n*, B*n*) are those of our installation reports; they are kept here so that
the scripts and the other pages can refer to them.

| Issue | Where | Effect | Workaround |
| :-- | :-- | :-- | :-- |
| [R3](#r3-meshroom_batch--i-keeps-only-the-last-folder) | Meshroom `meshroom_batch` | only the last image folder is imported | one comma-separated value (`scripts/run_template.sh`) |
| [R4](#r4-mrsegmentation-no-module-named-openimageio) | mrSegmentation (PR #85) | `ImageSegmentationSam3` fails | install OpenImageIO in its environment |
| [R5](#r5-lino-unips-fails-on-gpus-older-than-ampere) | LINO-UniPS | no LINO template on GPUs < 8.0 | none (use an Ampere or newer GPU) |
| [R6](#r6-black-texture-at-low-resolution) | Texturing | black texture at low resolution | none yet; full resolution not affected as far as we know |
| [B14](#b14-led-getter-nodes-fail-with-a-numpy-1x-error) | AliceVision bindings / mrLedGetter | LED-getter nodes fail | in the templates (`ConvertSfMFormat` node) |
| [B17](#b17-ledgetterlights-discards-poses-at-low-resolution) | mrLedGetter | poses discarded, holes in the mesh at low resolution | none at full resolution |
| [Other issues](#other-issues) | install | | |

## R3: `meshroom_batch -i` keeps only the last folder

`meshroom_batch -i MV PS/PS_01 PS/PS_02` imports only `PS/PS_02`, without any message, and the computation goes on
with a fraction of the images (biface: 13 images instead of 240). `parseInitInputs()` (`bin/meshroom_batch`) stores
each value under the same key. **Workaround:** pass all the folders as one comma-separated value,
`-i MV,PS/PS_01,PS/PS_02`, as `scripts/run_template.sh` does. `-I` (recursive import) alone imports nothing (B11).

## R4: mrSegmentation: `No module named 'OpenImageIO'`

`ImageSegmentationSam3` fails at `segmentationRDS/image.py: import OpenImageIO`: the plugin (PR #85) does not declare
OpenImageIO, and neither the nightly bundle nor a build from source provides its Python module to the plugin
environment. **Workaround** ([INSTALL.md, step 4](INSTALL.md#4-plugins)):

```bash
uv pip install --python $MESHROOM_LOCAL_PLUGINS_PATH/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
```

The bounds matter: every OpenImageIO wheel from 3.1.7 requires numpy 2, which breaks the AliceVision bindings of the
same environment (same mechanism as B14). An `update` of the plugin removes the fix.

## R5: LINO-UniPS fails on GPUs older than Ampere

On a Turing GPU (Quadro RTX 6000, compute capability 7.5), `LINOUniPS` fails on every pose with
`expected scalar type Half but found BFloat16`. The LINO-UniPS package switches its input to float16 below compute
capability 8.0, while parts of the network are hard-coded in bfloat16. The `[object]_lino_unips.mgt` templates
therefore need an Ampere (8.x), Ada or newer GPU. The LED-getter and Uni-MS-PS templates are not affected.

## R6: black texture at low resolution

On the 1000 px test sets, the `Texturing` node ends in SUCCESS but writes an almost black texture (biface LED-getter:
0 % of non-black texels; warrior LINO: 1 %). It does not depend on the machine nor on the AliceVision build. Tests
point to the density of the mesh relative to the size of the albedo texels (500 px albedo maps): decimating the mesh
brings the texture back. Not seen on the full-resolution reconstructions of the paper; the templates are unchanged.

## B14: LED-getter nodes fail with a numpy 1.x error

`LedGetterLights` fails with `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`, followed by a
`JSONDecodeError` that hides the cause. The environment of mrLedGetter has numpy 2, while the AliceVision Python
bindings of the nightly bundle (November 2026) are built against numpy 1. **Workaround, in the templates:** the
LED-getter templates convert the SfMData to `.sfm` JSON with a `ConvertSfMFormat` node in front of `LedGetterLights`
and `LedGetterPS`, so that these nodes do not read it through the bindings. The node stays in the templates until the
bindings or the plugin are fixed. Projects made from an earlier version of the templates need the same node.

## B17: LedGetterLights discards poses at low resolution

`LedGetterLights` drops a pose when fewer than 50 sampled pixels of its mask see the proxy mesh
(`MIN_PIXELS = 50` in `LedGetterLights.py`, not exposed as an input). The count is absolute: on the 1000 px biface
set, 2 of the 6 calibrated poses fall below it (38 and 48), and the RNb-NeuS2 mesh has holes on the faces they see. At
full resolution (8288 px) the poses have about 65 times more samples and the threshold is not reached.

## Other issues

| | Issue | Workaround |
| :-- | :-- | :-- |
| B7 | `meshroom_compute` with a relative project path | absolute path (`scripts/run_template.sh`) |
| B9 | USD resources missing from the AliceVision nightly: `.usda` exports stop | [INSTALL.md, step 1](INSTALL.md#1-alicevision) |
| B10 | mrSegmentation (PR #85) pins PyTorch 2.5.1 + CUDA 12.4, without kernels for Blackwell GPUs (RTX 50xx) | expected, not tested |
| B12 | `meshroom_batch --paramOverrides` is applied after the images are imported, too late for `CameraInit` | `GROUP_CAMERA_FALLBACK=global scripts/run_template.sh …` (only for images without a body serial number, e.g. converted JPEG) |
| B13 | vocabulary tree and detection models missing from the AliceVision nightly and from source installs | [INSTALL.md, step 1](INSTALL.md#1-alicevision) |
| B15 | Open3D (mrLedGetter) needs `libusb-1.0.so.0` | install `libusb-1.0` |
| B16 | segmentation fault at `import sphericart.jax` (mrLedGetter) when no unversioned `libcudart.so` / `libnvrtc.so` is on the library path | a CUDA 12 toolkit registered in `ld.so.conf`, or links `libcudart.so`, `libnvrtc.so` in `mrLedGetter/venv/lib/` to the `.so.12` of the `nvidia-*` wheels |
| | `meshroom_plugins` without a terminal: `EOFError` | `-f` |
| | the `.mgt` files record no plugin version: a template opens without warning with other plugin versions | compare with [tested versions](TESTED_VERSIONS.md) |
