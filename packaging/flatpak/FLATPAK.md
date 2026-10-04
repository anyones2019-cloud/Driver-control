# Driver-control Tools Flatpak

This is a separate program from the driver helper. It does not install a driver.

The tools program and `scripts/driver_link.py` share `drivers/old-gpu-catalog.json`. When a card is picked, the tools program writes `~/.local/share/driver-control/selection.json`. The driver helper reads that file.

Build and install on Fedora, inside a Linux virtual machine:

```bash
flatpak install -y flathub org.gnome.Platform//51 org.gnome.Sdk//51
flatpak-builder --user --install --force-clean build packaging/flatpak/io.github.anyones2019.DriverControlTools.yml
flatpak run io.github.anyones2019.DriverControlTools
```

Then, on the driver side:

```bash
python3 scripts/driver_link.py
```

`python3 scripts/driver_link.py --install` refuses to install.

## Window managers

The tools use GTK 4.24. Wayland is tried first, then X11.

- Wayland compositors: Hyprland, Sway, river, niri, wayfire, labwc, GNOME, and KDE Plasma on Wayland.
- X11 window managers: i3, bspwm, awesome, dwm, Openbox, Fluxbox, IceWM, Xfce, MATE, and KDE Plasma on X11.

Hyprland sets `HYPRLAND_INSTANCE_SIGNATURE`. The program treats that as Wayland and still keeps an X11 fallback.
