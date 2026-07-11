#!/usr/bin/env python3
"""Live ground-station monitor for the Jenga OBC UART telemetry.

Reads the ASCII frames streamed by the iCEstick build
("JGA n=.. s=.. b=.. p=.. z=.. f=..", 115200 8N1 on the board's second
FTDI serial port) and prints them decoded and annotated. Stdlib only.

Usage:
    python3 tools/telemetry_monitor.py [/dev/ttyUSB1]

Stop with Ctrl-C.
"""

from __future__ import annotations

import glob
import os
import re
import select
import sys
import termios

FRAME_RE = re.compile(
    r"JGA n=([0-9A-F]{4}) s=([01]) b=([01]) "
    r"p=([0-9A-F]{4}) z=([0-9A-F]{4}) f=([0-9A-F]{4})"
)


def open_port(dev: str) -> int:
    fd = os.open(dev, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0  # iflag: raw
    attrs[1] = 0  # oflag: raw
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0  # lflag: raw
    attrs[4] = attrs[5] = termios.B115200
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def main() -> int:
    if len(sys.argv) > 1:
        dev = sys.argv[1]
    else:
        candidates = sorted(glob.glob("/dev/ttyUSB*"))
        if not candidates:
            print("no /dev/ttyUSB* device found — is the iCEstick connected?")
            return 1
        dev = candidates[0]

    fd = open_port(dev)
    print(f"Jenga ground station — listening on {dev} at 115200 8N1 (Ctrl-C to stop)",
          flush=True)
    print(f"{'frame':>6} {'orbit phase':<12} {'burst rail':<11} "
          f"{'CAN fwd':>8} {'RLE words':>10} {'FIR samp':>9}", flush=True)

    buf = b""
    last_sun = None
    try:
        while True:
            r, _, _ = select.select([fd], [], [], 0.5)
            if not r:
                continue
            try:
                buf += os.read(fd, 4096)
            except OSError:
                continue
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                m = FRAME_RE.search(line.decode("ascii", "replace"))
                if not m:
                    continue
                n, s, b_, p, z, f = m.groups()
                sun = s == "1"
                phase = "SUNLIGHT" if sun else "ECLIPSE"
                if last_sun is not None and sun != last_sun:
                    event = "sunrise" if sun else "eclipse entry — comms/burst rails shed"
                    print(f"{'':>6} --- {event} ---", flush=True)
                last_sun = sun
                print(f"{int(n, 16):>6} {phase:<12} "
                      f"{'ON' if b_ == '1' else 'off':<11} "
                      f"{int(p, 16):>8} {int(z, 16):>10} {int(f, 16):>9}"
                      + ("   <- compression gated off" if not sun else ""),
                      flush=True)
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
