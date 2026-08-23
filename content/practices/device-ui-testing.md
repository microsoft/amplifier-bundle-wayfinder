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

Your UI fix passes the unit tests. `curl` against the server comes back clean. And then a human opens the app and it's visibly broken — a button off-screen, a dialog swallowed by the keyboard, a tap that lands on nothing. Server-side green tells you nothing about what rendered. These two bundles drive the real emulator/simulator and check the actual screen, resolving every tap against the accessibility tree instead of guessing at screenshot pixels.

**In practice:** you changed the login screen and want proof it still works on a real Android build. You hand it to the android-tester agents: boot the emulator, install the APK, `ui_dump` the live accessibility tree, `find` the "Sign in" node, tap *that node* (not an x/y guess), then assert the next screen actually appeared. Same discipline on iOS through the ios-tester agents against a simulator. Whatever the platform, run the bundle's `doctor` first — it reports every host problem at once with a fix for each.

**How to invoke:** delegate through the bundle's `android-*` / `ios-*` agents — don't drive `adb`/`simctl` by hand. The agents carry the selector-first discipline; raw shell driving throws it away.

**Install — two separate bundles.** Neither is built in. Check what's present with `amplifier bundle list`; if `android-tester` / `ios-tester` aren't there, add the one(s) you need. An explicit request to install or run a tester authorizes that in-scope action without duplicate Wayfinder ack; native host, tool, safety, and destructive-action approvals still apply. If Wayfinder introduces installation or testing as an optional next step, show the exact action and wait for explicit ack; never act unsolicited.

- `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-android-tester@main#subdirectory=behaviors/android-tester.yaml --app`
- `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-ios-tester@main#subdirectory=behaviors/ios-tester.yaml --app`

**Android — strong local evidence:**

- **Selector-first, never screenshot coordinates.** Resolve taps against the tree (`ui_dump` / `find`); raw-coordinate taps are the trap. Measured on one host: `tap` used 1215× vs `tap_xy` 8×, zero failures across 4912 ops. A vision model's guess can land 60–90px outside the button, and the tap silently hits nothing.
- **Pin the serial on a shared box.** The wrong-emulator serial is THE trap — verify focus and package before acting.
- **ANRs interfere.** Use `dismiss_anr`, and `wait_for` for synchronization — never bare sleeps.

**iOS — from the bundle docs (not locally exercised here):**

- **Points vs pixels.** The tree reports points, screenshots report pixels, scale ~3×. Every geometric field comes back in both spaces, labeled — use the labeled field, never convert by hand.
- **Free device tier refuses taps.** The physical-device element list carries no geometry, so the tool refuses rather than guessing.

Deeper: each bundle ships three agents (operator / visual-tester / debugger). Android runs on aarch64 Linux; iOS drives a remote Mac over plain SSH (Xcode only — no Apple Developer account needed for the simulator tier).
