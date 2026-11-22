# Hardware compatibility strategy

**Status:** Proposed (Phase 1). The database format is defined here; testing
starts in Phase 4.

## Principles

1. **Never claim support without evidence.** Every component status other than
   `untested` must cite a test: the date, the Linbox build ID and kernel, who
   tested it, and a link to the report.
2. **The model is not enough.** One "ThinkPad T14 Gen 3" can ship with
   different Wi-Fi cards, panels or webcams. Records are keyed on
   **DMI product name plus SKU/board**, and component variants are listed
   explicitly.
3. **Fix upstream first.** Prefer documented kernel parameters, firmware from
   `linux-firmware`, or packaged quirks over custom drivers. Avoid
   out-of-tree DKMS modules: they need MOK enrollment under Secure Boot and
   break on kernel updates. Each one is a decision recorded in the model file.
4. **The database is data, in git, reviewed by pull request.** The
   `linbox-hardware` package ships a snapshot of it so that `linbox hardware`
   can work offline.

## Database layout

```
hardware/compatibility/
├── schema.md                       field reference (below)
└── models/<vendor>/<model-slug>.yaml
```

### Status values

| Status | Meaning |
|---|---|
| `untested` | No Linbox test yet. This is the default for every field. |
| `works` | Tested and works with the stock Linbox OS install. |
| `works-with-workaround` | Works after a documented, packaged or one-step workaround. |
| `partial` | Some function is missing (e.g. the mic works, mute LED doesn't). Details are required. |
| `broken` | Tested and does not work. |
| `not-present` | The hardware variant doesn't have this component. |

### Components tracked

Every model file records these components:

- CPU
- integrated and discrete GPU
- Wi-Fi
- Bluetooth
- webcam (including IPU6/sensor), microphone, speakers and headphone jack
- internal display, brightness keys and backlight
- touchpad and TrackPoint
- keyboard hotkeys and backlight
- suspend/resume (s2idle and deep), hibernate
- external display (USB-C/DP and HDMI)
- battery reporting and charge thresholds
- fingerprint reader
- card reader, Ethernet
- USB-C docks
- firmware updates through fwupd/LVFS
- UEFI and Secure Boot
- TPM (for the installer's TPM-FDE)

Each component has:

- `status`
- `device`: the PCI or USB ID, driver and firmware file
- `notes`
- `workaround`
- `tests`: the list of evidence entries

## Webcams: Intel IPU6 and OV02C10

Many 12th/13th-gen Intel laptops use MIPI cameras through the **Intel IPU6**
image processor instead of a USB UVC webcam. Those need:

- the IPU6 kernel drivers
- a sensor driver (e.g. **OV02C10**)
- a userspace path, either the libcamera software ISP or Intel's camera HAL
  stack, with a v4l2 loopback or PipeWire bridge so ordinary apps can use the
  camera

How much of that works out of the box on Debian 13's 6.12 kernel (or a backports kernel) is
**unverified**. We mark it `untested` everywhere until a Linbox build is tested
on each specific model. Test procedure (Phase 4):

1. Check `lspci -nn` for the IPU device and `dmesg` for `intel-ipu6` and
   sensor probe messages.
2. Check `media-ctl` / `v4l2-ctl --list-devices`, and libcamera's `cam -l`.
3. Test video in a browser (WebRTC test page), in a PipeWire-aware app, and
   with `ffplay`.
4. Record the exact packages involved. Any non-archive packages require an
   architecture decision before we ship them.

## How `linbox hardware` uses it (Phase 4)

`linbox hardware`:

1. collects DMI, `lspci`/`lsusb` IDs, loaded drivers, firmware load errors and
   battery data (read-only, no root needed except where noted)
2. matches the result against the snapshot DB
3. prints known limitations and workarounds for this exact model
4. with `--report`, writes a redacted file the user can attach to a support
   ticket or a DB pull request. It never uploads anything automatically.

## First models

| Model | Role | Status |
|---|---|---|
| Infinix ZeroBook (i9-13900H, Iris Xe, 32 GB, NVMe, Intel Wi-Fi) | Development and validation machine | All `untested`: [models/infinix/zerobook-i9-13900h.yaml](../hardware/compatibility/models/infinix/zerobook-i9-13900h.yaml) |
| Lenovo ThinkPad T-series, Dell Latitude, HP EliteBook | Commercial targets | Pick specific generations once stock is known (Phase 4) |
