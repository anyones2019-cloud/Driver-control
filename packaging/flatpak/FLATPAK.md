# Driver-control Tools Flatpak

This is a separate program from the driver helper. It does not install a driver.

The tools program and `scripts/driver_link.py` share `drivers/old-gpu-catalog.json`. When a card is picked, the tools program writes `~/.local/share/driver-control/selection.json`. The driver helper reads that file.

Build and install on Fedora, inside a Linux virtual machine:

```bash
flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak-builder --user --install --force-clean build packaging/flatpak/io.github.anyones2019.DriverControlTools.yml
flatpak run io.github.anyones2019.DriverControlTools
```

Then, on the driver side:

```bash
python3 scripts/driver_link.py
```

`python3 scripts/driver_link.py --install` refuses to install.
