# Yandex Music release synchronization recovery

Status checked on 2026-10-06. Yandex Music v3.8.12 is published, but its
integration and upstream-branch synchronization did not finish.

## Confirmed failure

[Pipeline 37478029289](https://github.com/trudenboy/ma-provider-yandex-music/actions/runs/37478029289)
passed tests, lint and type checks and created the release. Both synchronization
jobs failed while regenerating `requirements_all.txt`, before commit and push.
The generator chooses the first requirement for a package. KION Music sorts
before Yandex Music and still requires `yandex-music==3.0.0`; Yandex Music
v3.8.12 requires `yandex-music==3.1.0`. The pin-consistency guard correctly
rejects the generated 3.0.0 requirement.

The failure is tracked in
[issue #259](https://github.com/trudenboy/ma-provider-yandex-music/issues/259).
A local run of MA's actual requirements generator with the two published
manifests reproduced 3.0.0. Aligning KION Music's manifest produced 3.1.0.

## Prepared source change

The KION Music change is limited to updating its manifest requirement to
`yandex-music==3.1.0` and adding a 3.0.10 changelog entry. Its maintainer-owned
`VERSION` stays unchanged. The existing KION Music working directory has
uncommitted work, so preparation used an independent checkout of its `dev`.

Full KION validation is still blocked by existing compatibility problems:

- On the current Yandex Music MA baseline, KION imports the removed
  `BYPASS_THROTTLER` symbol. The relevant incoming change is
  [KION PR #188](https://github.com/trudenboy/ma-provider-kion-music/pull/188).
- KION's `uv sync --locked --extra test` rejects its stale lockfile.
  Installing its frozen lock instead reaches another pre-existing import
  mismatch: `CONF_ENTRY_UNOFFICIAL_PROVIDER` is missing in that old MA build.

The manifest correction therefore has a passing requirements-generator check,
but does not yet have a passing KION test suite. It should be reviewed together
with KION's incoming compatibility changes, rather than treated as a completed
production repair.

## Recovery order

1. Resolve and validate KION's pending MA compatibility changes, then publish
   and review its dependency-pin change. Obtain maintainer approval before
   merging; apply a version bump only through the maintainer's release process.
2. Confirm the KION pipeline and its integration sync succeed. Read the target
   manifest and generated requirements to verify 3.1.0 actually arrived.
3. Use the existing workflow path to prepare KION's upstream change for human
   review. Upstream MA's KION manifest also still pins 3.0.0; integration sync
   alone cannot repair the separate Yandex upstream-branch pin conflict.
4. Once the sibling pin is aligned in each target baseline, rerun the Yandex
   v3.8.12 synchronization through the provider workflows. Keep the upstream
   preflight and pin-consistency guards enabled.
5. Verify the workflow results and target manifests, generated requirements
   and provider version. Review incident closure only after durable target
   state confirms delivery.

The rotor-session and browse refactors are independently validated local work;
they do not change this dependency conflict or publish a new release.
