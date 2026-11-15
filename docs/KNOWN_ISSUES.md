# Known issues

November 2026, [tested versions](TESTED_VERSIONS.md). Labels (R*n*, B*n*, J*n*, N*n*) are those of our test reports.

| | Issue | Fix |
| :-- | :-- | :-- |
| [R3](#r3-meshroom_batch--i-keeps-only-the-last-folder) | `meshroom_batch -i` imports only the last folder | in `scripts/run_template.sh` |
| [R4](#r4-mrsegmentation-no-module-named-openimageio) | mrSegmentation: `No module named 'OpenImageIO'` | one command, [INSTALL.md](INSTALL.md#2-alicevision-resources-and-plugins) |
| [R5](#r5-lino-unips-fails-on-gpus-older-than-ampere) | LINO-UniPS fails on GPUs older than Ampere | none |
| [R6](#r6-black-texture-at-low-resolution) | black texture at low resolution | none needed at full resolution |
| [B14](#b14-led-getter-nodes-fail-with-a-numpy-1x-error) | LED-getter nodes: numpy 1.x error | in the templates |
| [B17](#b17-ledgetterlights-discards-poses-at-low-resolution) | poses discarded at low resolution | none needed at full resolution |
| [J1](#j1-mrledgetter-does-not-install-on-glibc-234) | mrLedGetter does not install on glibc 2.34 | patched copy of the plugin |
| [Others](#other-issues) | | |

## R3: `meshroom_batch -i` keeps only the last folder

`meshroom_batch -i MV PS/PS_01 PS/PS_02` imports only `PS/PS_02`, silently. Pass one comma-separated value,
`-i MV,PS/PS_01,PS/PS_02`, as `scripts/run_template.sh` does.

## R4: mrSegmentation: `No module named 'OpenImageIO'`

PR #85 does not declare OpenImageIO. Install it, keeping numpy 1 for the AliceVision bindings (OpenImageIO ≥ 3.1.7
needs numpy 2); redo it after any `update` of the plugin:

```bash
uv pip install --python $P/mrSegmentation/venv/bin/python "numpy==1.26.4" "OpenImageIO<3.1.7"
```

## R5: LINO-UniPS fails on GPUs older than Ampere

`expected scalar type Half but found BFloat16` on every pose on compute capability < 8.0 (e.g. Quadro RTX 6000).
The `*_lino_unips.mgt` templates need an Ampere or newer GPU; the other templates are not affected.

## R6: black texture at low resolution

On 1000 px images, `Texturing` succeeds but writes an almost black texture. Not seen at full resolution.

## B14: LED-getter nodes fail with a numpy 1.x error

`A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x` in `LedGetterLights`: the AliceVision
bindings of the nightly builds use numpy 1, mrLedGetter numpy 2. The LED-getter templates avoid it with a
`ConvertSfMFormat` node (SfMData as `.sfm` JSON). Projects made from older templates need the same node.

## B17: LedGetterLights discards poses at low resolution

A pose with fewer than 50 sampled mask pixels on the proxy mesh is dropped (`MIN_PIXELS = 50`, not an input): holes
in the mesh on 1000 px images. All the poses are kept at full resolution.

## J1: mrLedGetter does not install on glibc 2.34

`UV command failed (exit code 2)` on RHEL / Rocky Linux 9: uv picks Open3D 0.20, whose wheels need glibc 2.35.
Install a copy constrained to Open3D 0.19 (tested on Rocky Linux 9):

```bash
git clone --depth 1 --branch v1.0.2 https://github.com/meshroomHub/mrLedGetter.git mrLedGetter-v1.0.2
sed -i '/^package = false/a constraint-dependencies = ["open3d<0.20"]' mrLedGetter-v1.0.2/pyproject.toml
rm -rf mrLedGetter-v1.0.2/.git && zip -qr $PWD/mrLedGetter-v1.0.2-open3d019.zip mrLedGetter-v1.0.2
```

Save as `$P/ledGetterOpen3d019.json`, then `$MP install -f mrLedGetterO3d019` (it installs into `$P/mrLedGetter`):

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

## Other issues

| | Issue | Fix |
| :-- | :-- | :-- |
| N1 | bundle: `install -f mrRNbNeuS2` reports success without the RNb-NeuS2 testbed | [INSTALL.md, step 2](INSTALL.md#2-alicevision-resources-and-plugins) |
| B13 | vocabulary tree and detection models missing from the nightly builds | [INSTALL.md, step 2](INSTALL.md#2-alicevision-resources-and-plugins) |
| J5 | bundle: `No module named 'chunk'` (SDMatte) at each command | harmless, no template uses it |
| B9 | AliceVision nightly older than `92b5846f`: `Failed to find the plugInfo.json …` | newer nightly |
| B7 | `meshroom_compute` fails with a relative project path | absolute path (`scripts/run_template.sh`) |
| B12 | `meshroom_batch --paramOverrides` too late for `CameraInit` | `GROUP_CAMERA_FALLBACK=global scripts/run_template.sh …` (images without a body serial number only) |
| B10 | mrSegmentation (PR #85): PyTorch without kernels for Blackwell (RTX 50xx) | expected, not tested |
| B15 | Open3D needs `libusb-1.0.so.0` | `sudo apt install libusb-1.0-0` |
| B16 | segfault at `import sphericart.jax` (mrLedGetter) without an unversioned `libcudart.so` | CUDA 12 toolkit in `ld.so.conf` |
| | `EOFError` from `meshroom_plugins` without a terminal | `-f` |
| | `FeatureMatching`, `StructureFromMotion` upgraded silently with the nightly builds | expected |
| | 12 warnings `Detected color space linear is not supported` in `Texturing` | harmless |
| | `MeshRemoveUnseenFaces` leaves open borders where no viewpoint sees the object (warrior base, calathos back) | expected |
