# Changelog

Changes of the templates, of the installation guide and of the tested versions. Most recent first.

## Unreleased

- Installation guide: the Meshroom nightly bundle as a second way (way A); the RNb-NeuS2 testbed installed by hand
  with it ([N1](KNOWN_ISSUES.md#other-issues)); the USD resources are no longer needed from the AliceVision nightly
  `92b5846f` ([B9](KNOWN_ISSUES.md#other-issues)); glibc 2.35 or newer for mrLedGetter, workaround for glibc 2.34
  ([J1](KNOWN_ISSUES.md#j1-mrledgetter-does-not-install-on-glibc-234)); disk and GPU memory of the full-resolution
  runs.
- `scripts/run_template.sh`: `MESHROOM_BUNDLE` runs the commands of the nightly bundle.
- `scripts/check_templates.py`: works with the Python of the nightly bundle.

## 2026-11-12

- First version of the repository: Meshroom templates of the VISART dataset in the `.mgt` format of Meshroom develop,
  template generator, installation guide, known issues.
- LED-getter templates (`warrior`, `biface`, `calathos`, `gourdan_bone_led_getter`): a `ConvertSfMFormat` node in front
  of `LedGetterLights` and `LedGetterPS` ([B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error)).
- Tests: fresh installation with the Meshroom plugin manager and end-to-end runs of `biface_visart-eccv26.mgt` and
  `warrior_lino_unips.mgt` on two machines ([tested versions](TESTED_VERSIONS.md)).
