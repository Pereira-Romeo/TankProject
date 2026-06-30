#!/usr/bin/env python3
"""
find_controller_mac.py

Automatically scans for nearby Bluetooth devices and finds the MAC address
of a specific controller type, based on the names controllers typically
report during discovery.

USAGE:
    python3 find_controller_mac.py --ps3
    python3 find_controller_mac.py --ps4
    python3 find_controller_mac.py --ps5
    python3 find_controller_mac.py --xbox

While the script is running, put the controller into Bluetooth pairing mode:
    PS4 / PS5  -> hold PS button + Share/Create button until light flashes fast
    Xbox       -> hold Xbox button, then hold small pair button until it flashes fast
    PS3        -> connects via USB, not Bluetooth -- this script won't find it,
                  just plug it in directly

The script will print the MAC address as soon as a matching device is found,
along with the exact pair/trust/connect commands to run next.

NOTE: this only works for controller types that connect via Bluetooth
(PS4, PS5, Xbox). PS3 controllers in this project connect over USB, so there
is nothing to scan for -- just plug it in.

Requires bluetoothctl to be installed and the Bluetooth service running:
    sudo systemctl start bluetooth
"""

import argparse
import re
import subprocess
import sys
import time

# Name substrings (lowercase) used to recognize each controller type from
# its Bluetooth advertised name. Same hints as used in tank.py's detection,
# since these are the names the controllers themselves broadcast.
NAME_HINTS = {
    "ps3":  ["playstation(r)3", "ps3", "sixaxis", "dualshock 3"],
    "ps4":  ["wireless controller", "ps4", "dualshock 4"],
    "ps5":  ["dualsense", "ps5", "dualshock 5", "playstation 5"],
    "xbox": ["xbox", "x-box", "xinput", "microsoft"],
}

DEVICE_LINE_RE = re.compile(r"\[NEW\] Device ([0-9A-Fa-f:]{17}) (.+)")

TIMEOUT_SECONDS = 60


def matches(name, controller_type):
    lowered = name.lower()
    return any(hint in lowered for hint in NAME_HINTS[controller_type])


def main():
    parser = argparse.ArgumentParser(
        description="Scan for a Bluetooth controller and print its MAC address."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ps3", action="store_true", help="Look for a PS3 controller (note: PS3 is USB, not Bluetooth)")
    group.add_argument("--ps4", action="store_true", help="Look for a PS4 (DualShock 4) controller")
    group.add_argument("--ps5", action="store_true", help="Look for a PS5 (DualSense) controller")
    group.add_argument("--xbox", action="store_true", help="Look for an Xbox controller")
    args = parser.parse_args()

    if args.ps3:
        controller_type = "ps3"
    elif args.ps4:
        controller_type = "ps4"
    elif args.ps5:
        controller_type = "ps5"
    else:
        controller_type = "xbox"

    if controller_type == "ps3":
        print("PS3 controllers in this project connect via USB, not Bluetooth.")
        print("Just plug it in directly -- there is no MAC address to find.")
        return

    print(f"Looking for a {controller_type.upper()} controller over Bluetooth...")
    print("Put the controller into pairing mode now.")
    print(f"(Scanning for up to {TIMEOUT_SECONDS} seconds. Ctrl+C to stop early.)\n")

    # Launch bluetoothctl as a subprocess and feed it commands via stdin,
    # then read its stdout live to catch [NEW] Device lines as they appear.
    proc = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # line-buffered
    )

    def send(cmd):
        proc.stdin.write(cmd + "\n")
        proc.stdin.flush()

    send("power on")
    time.sleep(0.5)
    send("agent on")
    time.sleep(0.5)
    send("scan on")

    found_mac = None
    found_name = None
    start = time.time()

    try:
        while time.time() - start < TIMEOUT_SECONDS:
            line = proc.stdout.readline()
            if not line:
                continue

            match = DEVICE_LINE_RE.search(line)
            if match:
                mac, name = match.group(1), match.group(2).strip()
                if matches(name, controller_type):
                    found_mac = mac
                    found_name = name
                    break
                else:
                    print(f"  (seen: {name} -- {mac}, not a match)")

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        send("scan off")
        time.sleep(0.3)
        send("exit")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    if found_mac:
        print(f"\nFound {controller_type.upper()} controller: {found_name}")
        print(f"MAC address: {found_mac}\n")
        print("To pair, trust, and connect it, run:")
        print(f"  bluetoothctl pair {found_mac}")
        print(f"  bluetoothctl trust {found_mac}")
        print(f"  bluetoothctl connect {found_mac}")
    else:
        print(f"\nNo {controller_type.upper()} controller found within {TIMEOUT_SECONDS} seconds.")
        print("Make sure:")
        print("  - the controller is in pairing mode (light flashing rapidly)")
        print("  - Bluetooth is enabled: sudo systemctl start bluetooth")
        print("  - you're running this with enough permissions (try with sudo if it fails)")
        sys.exit(1)


if __name__ == "__main__":
    main()
