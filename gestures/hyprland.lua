-- Load from ~/.config/hypr/input.lua after Omarchy defaults.
-- Native trackpads only; Deskflow delivers a virtual mouse instead.
for _, fingers in ipairs({ 3, 4 }) do
  hl.gesture({ fingers = fingers, direction = "horizontal", action = "workspace" })
  hl.gesture({ fingers = fingers, direction = "up", action = function()
    hl.exec_cmd(os.getenv("HOME") .. "/.local/bin/wayland-gesture up")
  end })
  hl.gesture({ fingers = fingers, direction = "down", action = function()
    hl.exec_cmd(os.getenv("HOME") .. "/.local/bin/wayland-gesture down")
  end })
end
hl.config({ input = { touchpad = {
  natural_scroll = true,
  clickfinger_behavior = true,
  tap_to_click = true,
  drag_3fg = 0,
} } })

-- Thumb plus three fingers: pinch restores; spread clears the desktop.
hl.gesture({ fingers = 4, direction = "pinchin", action = function()
  hl.exec_cmd(os.getenv("HOME") .. "/.local/bin/wayland-gesture restore-desktop")
end })
hl.gesture({ fingers = 4, direction = "pinchout", action = function()
  hl.exec_cmd(os.getenv("HOME") .. "/.local/bin/wayland-gesture show-desktop")
end })
