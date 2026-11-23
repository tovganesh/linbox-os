# Tests

## Automated (CI: `.github/workflows/iso.yml`)

| Job | What it proves |
|---|---|
| `lint` | Build scripts and hooks pass `shellcheck`; Python tools compile. |
| `build` (×2) | The ISO builds from the pinned Debian snapshot. The build fails if any Xorg component is installed (hook `9000-linbox-assert-no-xorg`). |
| `reproducibility` | Two independent builds of the same commit produce identical package manifests. |
| `boot-test` | [`vm/boot-test.py`](vm/boot-test.py) boots the ISO in QEMU/OVMF **with Secure Boot enforced**. It checks that the live user can log in over serial, that `linbox-spike` is installed, that no Xorg packages or processes exist, and that SDDM autologin starts a Plasma **Wayland** session (`kwin_wayland`). It saves the serial log and a screenshot. |

## Manual (M1): install to disk with Calamares

Calamares has no unattended mode, so this step is manual for now.

1. Create a VM (UEFI, Secure Boot on, 4+ GB RAM, 30 GB disk). Use
   virt-manager with an `OVMF_CODE*.secboot.fd` firmware, Hyper-V Gen 2 with the
   "Microsoft UEFI Certificate Authority" template, or VirtualBox 7 with EFI and
   Secure Boot.
2. Boot the ISO and open **Install Debian** (Calamares) from the desktop.
   Use the default erase-disk partitioning.
3. Reboot into the installed system and run these commands. Record the
   results in the M1 PR:
   ```sh
   cat /usr/share/linbox/marker                                   # test package reached the target
   dpkg -l | grep -E 'xserver-xorg|live-boot'                     # expect: none
   loginctl show-session "$XDG_SESSION_ID" -p Type                # expect: Type=wayland
   mokutil --sb-state 2>/dev/null || sudo dmesg | grep -i 'secure boot'
   sudo apt update && apt list --upgradable                       # repo health
   ```
