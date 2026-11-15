# Changelog

Changes of the templates, of the installation guide and of the tested versions. Most recent first.

## Unreleased

- Tests at full resolution on three machines ([tested versions](TESTED_VERSIONS.md)).
- Installation: Meshroom nightly bundle or from source; shorter docs.
- `scripts/run_template.sh`: `MESHROOM_BUNDLE` for the nightly bundle; `scripts/check_templates.py` runs with its
  Python.

## 2026-11-12

- First version of the repository: Meshroom templates of the VISART dataset in the `.mgt` format of Meshroom develop,
  template generator, installation guide, known issues.
- LED-getter templates (`warrior`, `biface`, `calathos`, `gourdan_bone_led_getter`): a `ConvertSfMFormat` node in front
  of `LedGetterLights` and `LedGetterPS` ([B14](KNOWN_ISSUES.md#b14-led-getter-nodes-fail-with-a-numpy-1x-error)).
- Tests: fresh installation with the Meshroom plugin manager and end-to-end runs of `biface_visart-eccv26.mgt` and
  `warrior_lino_unips.mgt` on two machines ([tested versions](TESTED_VERSIONS.md)).
