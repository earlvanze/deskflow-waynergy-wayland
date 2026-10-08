# Magic Trackpad gestures across Deskflow

Recognize gestures on the Mac with BetterTouchTool, then route actions according
to Deskflow's latest active-screen log entry. The Linux receiver uses Hyprland
0.55+ Lua dispatchers and Omarchy's app launcher. SSH uses existing trusted keys;
there is no new network listener.

| Gesture | Linux action |
| --- | --- |
| Three or four fingers left / right | Next / previous workspace |
| Three or four fingers up | App launcher |
| Three or four fingers down | Empty desktop; repeat to restore previous workspace |
| Thumb + three fingers pinch inward | Restore previous windows |
| Thumb + three fingers spread outward | Clear screen / show empty desktop |

Mac-local swipes invoke Control+arrow shortcuts. Mac-local pinch/spread sends F11 (Show Desktop toggle). These require the corresponding macOS shortcuts
to be enabled. Two-finger scrolling and secondary clicks retain their existing
Deskflow behavior. The bridge does not transport raw multitouch, continuous
workspace animation, application pinch-to-zoom, or rotation. The launcher is not
a Mission Control window overview.

## Install

1. Put `deskflow-gesture` in the Mac's `~/.local/bin/` and `wayland-gesture` in
   the Linux user's `~/.local/bin/`; make both executable. Python 3 is required.
2. Configure trusted, passwordless SSH from the Mac to the Linux user, verifying
   the host key through your usual trusted enrollment process.
3. Create `~/.config/deskflow-gestures.json` on the Mac:

```json
{
  "server_screen": "my-mac",
  "log": "~/Library/Logs/Deskflow-sharing.log",
  "clients": { "my-linux-screen": "myuser@my-linux-host" }
}
```

Use the screen names from Deskflow's configuration and its actual log path.
Enable INFO logging with screen-switch messages. The router reads a bounded tail
of that log. Unknown clients, a missing route, and observed disconnects produce
no action. Deskflow must be running. A stale log after an unlogged server crash
can still misidentify the destination; restart/reconnect Deskflow before use.

4. Import `Deskflow-Wayland.bttpreset` into BetterTouchTool and enable the preset.
   On old BetterTouchTool releases that ignore file imports, use its legacy
   native URL importer and accept the import dialog:

```sh
python3 - <<'PY'
import base64, pathlib, subprocess
p = pathlib.Path('Deskflow-Wayland.bttpreset')
subprocess.run(['open', 'btt://jsonimport/' + base64.b64encode(p.read_bytes()).decode()], check=True)
PY
```

Import once. Legacy BTT can duplicate even complete presets with the same UUID.
When replacing a preset, disable the previous copy so exactly one is active.
A complete preset is included so it can be disabled as a unit. Review overlapping BTT
bindings and macOS gesture assignments if both systems respond to one swipe.
Keep existing BTT configuration; do not replace its database.

5. After enabling the BTT preset, run `python3 mac-system-gestures.py` on the
   Mac. It saves only the affected preference keys, disables conflicting native
   gestures, and restarts the Dock. Keyboard shortcuts stay available for the
   local gesture actions. To roll back, run it with `--restore`.
6. Run `~/.local/bin/deskflow-gesture left --dry-run` on the Mac to inspect the
   destination. With the pointer on Linux, swipe in both directions and verify
   that Mac Spaces stay unchanged. Test each finger count separately.

## Directly connected trackpads

For a trackpad paired directly to Linux, install `hyprland.lua` as
`~/.config/hypr/gestures.lua` and add `require("hypr.gestures")` to the user
`input.lua`. The receiver must still be installed for the up/down actions.
This enables native three- and four-finger workspace gestures, four-finger
pinch/spread for restore/show desktop, natural scrolling,
tap-to-click and finger-count secondary clicks. Three-finger dragging is disabled
to avoid conflicting with three-finger swipes. Reload and validate:

```sh
hyprctl reload
hyprctl configerrors
```

## Verification and rollback

`python3 -m unittest discover -s gestures -v` checks routing isolation, disconnect
handling, SSH destination validation, swipe direction and brightness press/release
mapping consistency. On the initial deployment, a real Mac-to-Linux SSH command
switched a workspace and show-desktop restored the previous workspace. BTT 2.428
persisted all ten gesture/action mappings via its native importer. Physical
finger recognition and local Mac shortcut behavior still require a hardware test.

Disable the BTT preset and run `python3 mac-system-gestures.py --restore`
to restore prior Mac gesture handling. Remove the
`require("hypr.gestures")` line to disable native Linux gestures. User-specific
configuration, keys and recovery copies stay outside this repository.

Sources: [Deskflow multitouch discussion](https://github.com/deskflow/deskflow/discussions/9437),
[BTT URL import](https://docs.folivora.ai/docs/scripting/url-scheme/),
[BTT gesture IDs](https://docs.folivora.ai/docs/json/trigger-definitions/),
[Hyprland gestures](https://wiki.hypr.land/Configuring/Advanced-and-Cool/Gestures/).

The Linux receiver reconstructs the Omarchy, D-Bus and display environment for
SSH sessions. Launcher actions require this even when workspace switching already
works. On the Mac, the last 20 action-start/completion/failure events are in
`~/.cache/deskflow-gesture-events.json`; this helps distinguish a gesture that
was not recognized from an action that failed. It contains no keyboard text.
After changing system pinch preferences, restart BetterTouchTool to refresh its
recognizer. The restore/show-desktop pair uses **thumb plus three fingers**;
two-finger application zoom is not mapped by this bridge.

### Legacy BetterTouchTool action execution

The preset uses background terminal action **137**, not shell-task action 206.
On the initial BTT 2.428 deployment, its shell-task XPC runner reported an error
before the router wrote any diagnostic event. Merely testing the router through
SSH does not validate execution through BetterTouchTool.

If thumb-plus-three pinch/spread is never recognized, inspect Advanced Settings
→ Trackpad → Thumb/Palm Handling. Disable palm recognition for a controlled test
and preserve the old setting for rollback. Recognition failures and a workaround
are discussed in the [BTT support thread](https://community.folivora.ai/t/launchpad-shortcut-with-trackpad-how-can-i-customise-it-or-disable-it-macos-26/45525/20).
Physical recognition after this adjustment remains subject to hardware validation.

On Linux, spreading repeatedly keeps the screen clear; pinching repeatedly after
restoring does nothing. Swiping away from the empty desktop cancels the automatic
return behavior so a later pinch does not unexpectedly switch workspaces.
