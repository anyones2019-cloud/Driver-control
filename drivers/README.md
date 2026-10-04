# Old GPU drivers

Catalog only. This repo does not ship NVIDIA, AMD, or Intel driver binaries.
Those files are proprietary. Testers download them from the vendor, then try them in a Linux VM.

Open-source options are already in the Linux kernel and Mesa: nouveau, radeon, amdgpu, i915.

## NVIDIA legacy branches

- 470.xx: Kepler (GeForce 600/700). Last legacy branch NVIDIA still lists.
- 390.157: Fermi (GeForce 400/500). Archive.
- 340.108: Tesla (GeForce 8/9/200/300). Archive.
- Official index: https://www.nvidia.com/en-us/drivers/unix/
- Archive: https://www.nvidia.com/en-us/drivers/unix/linux-display-archive/

## AMD old cards

- GCN 1.0 / 1.1 (HD 7000, R9 200): kernel drivers radeon and amdgpu, plus Mesa.
- Newer RX cards: amdgpu in the kernel. Proprietary packages are on AMD's site.
- Official: https://www.amd.com/en/support/download/linux-drivers.html

## Intel old GPUs

- i915 kernel driver covers older Intel integrated graphics.
- No separate vendor blob is required for basic display.

## VM test

1. Pick one card family from old-gpu-catalog.json.
2. Boot a Fedora VM. Do not use a main machine.
3. Try the open-source driver first.
4. Only if needed, download the matching legacy package from the vendor link.
5. Report card, driver branch, and pass or fail on the GitHub issue.
