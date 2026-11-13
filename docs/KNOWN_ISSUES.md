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
| [J1](#j1-mrledgetter-does-not-install-on-glibc-234) | mrLedGetter (Open3D) | does not install on glibc 2.34 (RHEL, Rocky Linux 9) | install a copy that constrains Open3D |
| [Other issues](#other-issues) | install | | |

## R3: `meshroom_batch -i` keeps only the last folder

`meshroom_batch -i MV PS/PS_01 PS/PS_02` imports only `PS/PS_02`, without any message, and the computation goes on
with a fraction of the images (biface: 13 images instead of 240). `parseInitInputs()` (`bin/meshroom_batch`) stores
each value under the same key. **Workaround:** pass all the folders as one comma-separated value,
`-i MV,PS/PS_01,PS/PS_02`, as `scripts/run_template.sh` does. `-I` (recursive import) alone imports nothing (B11).

## R4: mrSegmentation: `No module named 'OpenImageIO'`

`ImageSegmentationSam3` fails at `segmentationRDS/image.py: import OpenImageIO`: the plugin (PR #85) does not declare
OpenImageIO, and neither the nightly bundle nor a build from source provides its Python module to the plugin
environment. **Workaround** ([INSTALL.md, step 2](INSTALL.md#2-plugins)):

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

## J1: mrLedGetter does not install on glibc 2.34

`meshroom_plugins install -f mrLedGetter` fails after a few seconds with `UV command failed (exit code 2)` on glibc
2.34 (RHEL and Rocky Linux 9): mrLedGetter v1.0.2 has no lock file and no bound on Open3D, `uv` takes Open3D 0.20.0,
whose Linux wheels need glibc 2.35. Without the pull requests of the plugin manager (nightly bundle), the command
still exits with 0. **Workaround** (tested on Rocky Linux 9): install a copy of the plugin whose `pyproject.toml`
constrains Open3D to 0.19, from a local registry file:

```bash
git clone --depth 1 --branch v1.0.2 https://github.com/meshroomHub/mrLedGetter.git mrLedGetter-v1.0.2
sed -i '/^package = false/a constraint-dependencies = ["open3d<0.20"]' mrLedGetter-v1.0.2/pyproject.toml
rm -rf mrLedGetter-v1.0.2/.git && zip -qr $PWD/mrLedGetter-v1.0.2-open3d019.zip mrLedGetter-v1.0.2
```

then save as `$P/ledGetterOpen3d019.json` (`$P`: plugin folder, see [INSTALL.md](INSTALL.md#2-plugins)):

```json
{
    "name": "ledGetterOpen3d019",
    "description": "mrLedGetter v1.0.2 with open3d<0.20 (glibc 2.34)",
    "url": "",
    "entries": [
        {
            "name": "mrLedGetterO3d019",
            "url": "file:///path/to/mrLedGetter-v1.0.2-open3d019.zip",
            "versions": ["dev+open3d019"],
            "publisher": "meshroomHub",
            "description": "LED-getter, open3d < 0.20",
            "license": "MIT"
        }
    ]
}
```

and run `meshroom_plugins install -f mrLedGetterO3d019` (it installs into `$P/mrLedGetter`). The entry needs a name
of its own: without the pull requests, the official registry hides a local entry of the same name. With them, the
name `mrLedGetter` also works.

## Other issues

| | Issue | Workaround |
| :-- | :-- | :-- |
| B7 | `meshroom_compute` with a relative project path | absolute path (`scripts/run_template.sh`) |
| B9 | USD resources missing from the AliceVision nightly builds older than `92b5846f` (2026-11-12): `.usda` exports stop | a newer nightly build, [INSTALL.md](INSTALL.md#from-source) |
| B10 | mrSegmentation (PR #85) pins PyTorch 2.5.1 + CUDA 12.4, without kernels for Blackwell GPUs (RTX 50xx) | expected, not tested |
| B12 | `meshroom_batch --paramOverrides` is applied after the images are imported, too late for `CameraInit` | `GROUP_CAMERA_FALLBACK=global scripts/run_template.sh …` (only for images without a body serial number, e.g. converted JPEG) |
| B13 | vocabulary tree and detection models missing from the nightly builds (AliceVision and Meshroom bundle) and from source installs | [INSTALL.md, step 1](INSTALL.md#1-meshroom) |
| B15 | Open3D (mrLedGetter) needs `libusb-1.0.so.0` | install `libusb-1.0` |
| N1 | without the pull requests of the plugin manager (e.g. the Meshroom nightly bundle), `meshroom_plugins install -f mrRNbNeuS2` reports success without installing the RNb-NeuS2 testbed (only a warning `Invalid entry in 'assets'`) | [INSTALL.md, step 2](INSTALL.md#2-plugins) |
| J5 | Meshroom nightly bundle: `Failed to load … SDMatte.py … No module named 'chunk'` at each command (mrSegmentation PR #85 imports a module that the bundle's Python lacks) | none needed: no template uses `SDMatte` |
| B16 | segmentation fault at `import sphericart.jax` (mrLedGetter) when no unversioned `libcudart.so` / `libnvrtc.so` is on the library path | a CUDA 12 toolkit registered in `ld.so.conf`, or links `libcudart.so`, `libnvrtc.so` in `mrLedGetter/venv/lib/` to the `.so.12` of the `nvidia-*` wheels |
| | `meshroom_plugins` without a terminal: `EOFError` | `-f` |
| | the `.mgt` files record no plugin version: a template opens without warning with other plugin versions | compare with [tested versions](TESTED_VERSIONS.md) |
