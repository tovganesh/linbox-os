#!/usr/bin/env python3
"""Boot a Linbox OS live ISO in QEMU with UEFI Secure Boot and check the live session.

Checks (Milestone M1):
  * firmware boots the ISO with Secure Boot enforced (kernel reports it)
  * the live system reaches a serial login and the live user can log in
  * the Linbox test package is installed
  * no Xorg server package is installed and no Xorg process runs
  * SDDM autologin starts a Plasma *Wayland* session (kwin_wayland running)

The Calamares install to disk is NOT automated here; see tests/README.md.

Usage: boot-test.py ISO OUTDIR [--ovmf-code F] [--ovmf-vars F]
Requires: qemu-system-x86_64 with KVM, OVMF Secure Boot firmware (Debian/Ubuntu "ovmf").
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time

LIVE_USER, LIVE_PASS = "user", "live"  # live-config defaults


class Serial:
    def __init__(self, path, logfile):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        for _ in range(100):
            try:
                self.sock.connect(path)
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("cannot connect to serial socket")
        self.buf = ""
        self.lock = threading.Lock()
        self.log = open(logfile, "w", encoding="utf-8", errors="replace")
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        while True:
            try:
                data = self.sock.recv(4096)
            except OSError:
                return
            if not data:
                return
            text = data.decode("utf-8", errors="replace")
            self.log.write(text)
            self.log.flush()
            with self.lock:
                self.buf += text

    def send(self, text):
        self.sock.sendall(text.encode())

    def wait_for(self, pattern, timeout, start=0, flags=0):
        rx = re.compile(pattern, flags)
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.lock:
                m = rx.search(self.buf, start)
            if m:
                return m
            time.sleep(0.5)
        return None

    def mark(self):
        with self.lock:
            return len(self.buf)

    def run(self, cmd, timeout=120):
        """Run a shell command on the logged-in serial console; return (rc, output)."""
        tag = f"T{int(time.time() * 1000)}"
        pos = self.mark()
        self.send(f"echo {tag}-BEGIN; {cmd}; echo {tag}-END rc=$?\n")
        m = self.wait_for(rf"{tag}-BEGIN\r?\n(.*?){tag}-END rc=(\d+)", timeout, pos, re.S)
        if not m:
            return None, ""
        return int(m.group(2)), m.group(1).replace("\r", "").strip()


class Monitor:
    def __init__(self, path):
        self.path = path

    def cmd(self, line):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.path)
        s.recv(4096)
        s.sendall((line + "\n").encode())
        time.sleep(0.3)
        s.close()


def find_first(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso")
    ap.add_argument("outdir")
    ap.add_argument("--ovmf-code", default=find_first([
        "/usr/share/OVMF/OVMF_CODE_4M.secboot.fd", "/usr/share/OVMF/OVMF_CODE.secboot.fd"]))
    ap.add_argument("--ovmf-vars", default=find_first([
        "/usr/share/OVMF/OVMF_VARS_4M.ms.fd", "/usr/share/OVMF/OVMF_VARS.ms.fd"]))
    ap.add_argument("--memory", default="6144")
    ap.add_argument("--tcg", action="store_true",
                    help="software emulation (no KVM); much slower, timeouts scaled x4")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    if not (args.ovmf_code and args.ovmf_vars):
        print("E: Secure Boot OVMF firmware not found", file=sys.stderr)
        return 2
    vars_copy = os.path.join(args.outdir, "OVMF_VARS.fd")
    shutil.copyfile(args.ovmf_vars, vars_copy)
    serial_sock = os.path.join(args.outdir, "serial.sock")
    mon_sock = os.path.join(args.outdir, "monitor.sock")
    for p in (serial_sock, mon_sock):
        if os.path.exists(p):
            os.unlink(p)

    slow = 4 if args.tcg else 1
    accel = ["-accel", "tcg,thread=multi", "-cpu", "max"] if args.tcg else ["-enable-kvm", "-cpu", "host"]
    qemu = subprocess.Popen([
        "qemu-system-x86_64", *accel, "-smp", "4", "-m", args.memory,
        "-machine", "q35,smm=on", "-global", "driver=cfi.pflash01,property=secure,value=on",
        "-drive", f"if=pflash,format=raw,unit=0,readonly=on,file={args.ovmf_code}",
        "-drive", f"if=pflash,format=raw,unit=1,file={vars_copy}",
        "-drive", f"file={args.iso},media=cdrom,readonly=on",
        "-vga", "virtio", "-display", "none",
        "-serial", f"unix:{serial_sock},server,nowait",
        "-monitor", f"unix:{mon_sock},server,nowait",
        "-nic", "user,model=virtio-net-pci",
    ])
    results = {"checks": {}, "info": {}}

    def check(name, ok, detail=""):
        results["checks"][name] = {"ok": bool(ok), "detail": detail}
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}".rstrip(), flush=True)

    try:
        ser = Serial(serial_sock, os.path.join(args.outdir, "serial.log"))
        mon = Monitor(mon_sock)

        # Press Enter at the boot menu until the kernel starts printing.
        for _ in range(24 * slow):
            time.sleep(5)
            if ser.wait_for(r"Linux version", 0.1):
                break
            mon.cmd("sendkey ret")
        check("kernel boots", ser.wait_for(r"Linux version", 120 * slow))

        sb = ser.wait_for(r"[Ss]ecure boot (enabled|disabled)", 120 * slow)
        check("secure boot enforced", sb and sb.group(1) == "enabled", sb.group(0) if sb else "no message")

        login = ser.wait_for(r"\S+ login: ", 900 * slow)
        check("serial login prompt", login)
        if not login:
            raise RuntimeError("no login prompt")
        ser.send(LIVE_USER + "\n")
        ser.wait_for(r"[Pp]assword:", 30)
        ser.send(LIVE_PASS + "\n")
        check("live user login", ser.wait_for(r"user@\S+:\S*\$ ", 60))
        ser.run("export TERM=dumb PAGER=cat SYSTEMD_PAGER=cat SYSTEMD_COLORS=0")

        rc, out = ser.run("dpkg-query -W -f='${Package} ${Version}\\n' linbox-spike")
        check("linbox-spike installed", rc == 0 and "linbox-spike 0.1.0" in out, out)

        rc, out = ser.run("cat /usr/share/linbox/build-info.json")
        results["info"]["build_info"] = out

        rc, out = ser.run("dpkg-query -W -f='${binary:Package} ${Status}\\n' 'xserver-xorg*' 'xorg' 2>/dev/null"
                          " | grep 'install ok installed' || true")
        check("no Xorg packages", out == "", out)

        # Wait for SDDM autologin into the Plasma Wayland session.
        session = ""
        for _ in range(36 * slow):
            rc, out = ser.run(
                "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do "
                "loginctl show-session $s -p Name -p Type -p Service -p Class | paste -sd' '; done")
            # One line per session; property order is systemd's, not the -p order.
            if any("Name=user" in ln and "Service=sddm-autologin" in ln and "Type=wayland" in ln
                   for ln in out.splitlines()):
                session = out
                break
            time.sleep(5)
        check("plasma wayland session", session, session)

        rc, out = ser.run("pgrep -a kwin_wayland || true")
        check("kwin_wayland running", "kwin_wayland" in out, out[:200])
        rc, out = ser.run("pgrep -a -x Xorg || true")
        check("no Xorg process", out == "", out)
        rc, out = ser.run("pgrep -a Xwayland || true")
        results["info"]["xwayland"] = out
        rc, out = ser.run("sudo dmesg | grep -i 'secure boot' || true")
        results["info"]["dmesg_secureboot"] = out
        rc, out = ser.run("systemctl --failed --no-legend --plain || true")
        results["info"]["failed_units"] = out

        # Wake the display in case power management blanked it, then capture.
        mon.cmd("mouse_move 20 20")
        mon.cmd("sendkey shift")
        time.sleep(5)
        mon.cmd(f"screendump {os.path.join(args.outdir, 'screen.png')} -f png")
        time.sleep(2)
    except Exception as e:  # noqa: BLE001 - report and fail
        check("test harness", False, repr(e))
    finally:
        qemu.terminate()
        try:
            qemu.wait(20)
        except subprocess.TimeoutExpired:
            qemu.kill()

    ok = all(c["ok"] for c in results["checks"].values())
    results["result"] = "pass" if ok else "fail"
    with open(os.path.join(args.outdir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results["info"], indent=2))
    print("RESULT:", results["result"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
