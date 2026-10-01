# Deskflow → Waynergy on Wayland

A public, reusable configuration reference for sharing a macOS keyboard and
mouse with a Wayland desktop through **Deskflow** (server) and **Waynergy**
(client). It is tailored to an Apple keyboard and a wlroots compositor such as
Hyprland or Omarchy.

## What is included

- `waynergy-config.ini` — a working raw key map for a macOS Deskflow server.
  It covers ANSI keys, keypad, arrows, media/brightness keys, and Mac Fn
  navigation behavior:
  - `Fn`+`Delete` → Forward Delete
  - `Fn`+Left / Right → Home / End
  - `Fn`+Up / Down → Page Up / Page Down
- `waynergy-disabled-clipboard.patch` — small safety initialization patch for
  builds where the Waynergy clipboard resources are deliberately disabled.

## Requirements

- Deskflow running as the input-sharing **server** on macOS.
- Waynergy 0.0.17 or a compatible version running on the Wayland client.
- A wlroots compositor with virtual-keyboard support (for example Hyprland).
- Deskflow and Waynergy configured to use compatible TLS settings.

> [!IMPORTANT]
> This repository intentionally contains **no certificates, private keys,
> TLS fingerprints, live IP addresses, or personal host names**. Waynergy
> creates its local TLS material under `~/.config/waynergy/tls/`; keep that
> directory private.

## Install the Waynergy template

Copy the example, then replace the two identity placeholders:

```bash
mkdir -p ~/.config/waynergy
cp waynergy-config.ini ~/.config/waynergy/config.ini
$EDITOR ~/.config/waynergy/config.ini
```

Set:

```ini
host = deskflow-server.example
name = wayland-client
```

- `host` is the DNS name or address where Deskflow is listening.
- `name` must exactly match the client screen name in the Deskflow server
  layout.

The example enables TLS but deliberately uses `tofu = false`. Pin the server
certificate/fingerprint using your own trusted enrollment procedure, or enable
TOFU only if trusting the first observed server certificate is appropriate for
your network.

## systemd user service

A minimal client service, assuming the standard Wayland session environment:

```ini
# ~/.config/systemd/user/waynergy.service
[Unit]
Description=Waynergy Deskflow client
After=graphical-session.target
PartOf=graphical-session.target

[Service]
ExecStart=/usr/local/bin/waynergy -L info
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
```

For Hyprland, add the compositor socket environment when your user-systemd
session does not already inherit it:

```ini
# ~/.config/systemd/user/waynergy.service.d/wayland.conf
[Service]
Environment="WAYLAND_DISPLAY=wayland-1"
Environment="HYPRLAND_INSTANCE_SIGNATURE=%H"
```

Adjust the Waynergy binary path and `WAYLAND_DISPLAY` for your installation,
then enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now waynergy.service
journalctl --user -u waynergy.service -f
```

## Why the navigation mappings matter

The Apple keyboard's `Fn` layer does not transmit the physical key underneath.
Deskflow reports separate macOS navigation virtual keycodes. In particular,
`Fn`+`Delete` is **Forward Delete**, not Backspace. The raw mappings in the
example translate those events to Wayland/XKB keycodes:

| Mac input | Wayland result |
| --- | --- |
| Fn+Delete | Delete (forward delete) |
| Fn+Left / Fn+Right | Home / End |
| Fn+Up / Fn+Down | Page Up / Page Down |

## Troubleshooting

Check that the client is connected:

```bash
systemctl --user status waynergy.service
journalctl --user -u waynergy.service -n 100 --no-pager
```

For key mapping diagnosis, temporarily use `-L debugsyn` in `ExecStart`, restart
the service, press the affected key, and inspect `DKDN` / `DKUP` lines in the
journal. The remote Deskflow key code is the left side of `[raw-keymap]`; the
local XKB keycode is the right side.

On the macOS host, ensure `deskflow-core` has Accessibility and Input Monitoring
permission. Avoid starting multiple unmanaged Deskflow server instances at the
same time; use a single supervised service or the app, not both.

## License

MIT. Deskflow and Waynergy are separate projects with their own licenses.
