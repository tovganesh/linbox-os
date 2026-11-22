# Hardware model file schema (v1)

Each model is one YAML file at `models/<vendor>/<model-slug>.yaml`. The
strategy and status meanings are in
[docs/hardware-compatibility.md](../../docs/hardware-compatibility.md).

```yaml
schema: 1
vendor: string                 # marketing vendor name
model: string                  # marketing model name
dmi:                           # match keys from /sys/class/dmi/id
  sys_vendor: string
  product_name: string | null  # null = not yet captured
  product_sku: string | null
  board_name: string | null
role: development | commercial | community
specs:                         # nominal configuration of the tested unit
  cpu: string
  ram: string
  storage: string
components:
  <component-id>:              # see list below
    status: untested | works | works-with-workaround | partial | broken | not-present
    device: string | null      # e.g. "8086:a7a0 i915" or "USB 0bda:5634 uvcvideo"
    notes: string | null
    workaround: string | null  # required when status is works-with-workaround
    tests:                     # required when status is not untested / not-present
      - date: YYYY-MM-DD
        build: string          # Linbox build ID
        kernel: string
        tester: string
        report: string         # URL or repo path of the test report
known_limitations: [string]
```

Component IDs:

- `cpu`, `gpu_integrated`, `gpu_discrete`
- `wifi`, `bluetooth`, `ethernet`
- `webcam`, `microphone`, `speakers`, `headphone_jack`
- `display_internal`, `brightness`, `display_external_hdmi`,
  `display_external_usbc`
- `touchpad`, `trackpoint`, `keyboard_hotkeys`, `keyboard_backlight`
- `suspend_resume`, `hibernate`
- `battery`, `charge_thresholds`
- `fingerprint`, `card_reader`, `usb_c_dock`
- `firmware_updates`, `secure_boot`, `tpm`

A validator (`tools/`) checks files against this schema. It arrives with the
first CI in Phase 2.
