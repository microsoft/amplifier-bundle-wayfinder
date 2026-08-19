---
id: device-ui-testing
category: practice
headline: "Drive a real Android emulator or iOS simulator and verify what actually rendered — selector-first via the accessibility tree, never screenshot coordinates."
try_now:
  - 'amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-android-tester@main#subdirectory=behaviors/android-tester.yaml --app'
  - 'amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-ios-tester@main#subdirectory=behaviors/ios-tester.yaml --app'
signals:
  prompt_matches:
    - '\b(android[- ]?(test|tester|emulator)|ios[- ]?(test|tester|simulator)|test (an? )?app on (android|ios|an emulator|a simulator)|accessibility tree|ui[- ]?dump|dismiss[- ]?anr)\b'
trigger: "the user wants to drive or UI-test a mobile app on an Android emulator or iOS simulator, or verify what a mobile screen actually rendered"
action: 'read_file("@wayfinder:content/practices/device-ui-testing.md")'
provenance: "android-tester + ios-tester bundle announcements (2026-08) + spark-1 android session evidence; iOS tips from bundle docs (not locally exercised here)"
verified_at: 2026-08-19
---

# device UI testing — android-tester + ios-tester

**Boot an emulator/simulator, install and drive the app, and verify what rendered — resolving every tap against the accessibility tree, never against a screenshot.** Two bundles, one discipline. Delegate through the `android-*` / `ios-*` agents; don't drive adb/simctl by hand.

## Try it now

1. Android: `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-android-tester@main#subdirectory=behaviors/android-tester.yaml --app`
2. iOS: `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-ios-tester@main#subdirectory=behaviors/ios-tester.yaml --app`

Run the bundle's `doctor` first — it reports every host problem at once with a fix for each.

## Why it matters

A UI fix can pass unit tests and server-side curl and still be visibly broken the moment a human opens the app. These drive the real thing and check what actually rendered.

## Gotchas — Android (strong local evidence)

- **Selector-first, never screenshot coordinates.** Resolve taps against the tree (`ui_dump` / `find`); raw-coordinate taps are the trap. Measured on one host: `tap` used 1215× vs `tap_xy` 8×, zero failures across 4912 ops. A vision model's guess can land 60–90px outside the button, and the tap silently hits nothing.
- **Pin the serial on a shared box.** The wrong-emulator serial is THE trap — verify focus and package before acting.
- **ANRs interfere.** Use `dismiss_anr`, and `wait_for` for synchronization — never bare sleeps.

## Gotchas — iOS (from bundle docs; not locally exercised here)

- **Points vs pixels.** The tree reports points, screenshots report pixels, scale ~3×. Every geometric field comes back in both spaces, labeled — use the labeled field, never convert by hand.
- **Free device tier refuses taps.** The physical-device element list carries no geometry, so the tool refuses rather than guessing.

## More

- Each bundle ships three agents (operator / visual-tester / debugger). Android runs on aarch64 Linux; iOS drives a remote Mac over plain SSH (Xcode only, no Apple Developer account for the simulator tier).
