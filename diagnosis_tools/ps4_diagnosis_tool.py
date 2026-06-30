#!/usr/bin/env python3
"""
PS4 DualShock 4 controller (USB or Bluetooth) diagnostic tool.

--- Pairing the PS4 controller via Bluetooth (optional, skip if using USB) ---

    bluetoothctl
    power on
    agent on
    scan on
    # Hold the PS button + Share button until the lightbar flashes fast
    # When it appears in the scan list, note its MAC (e.g. AA:BB:CC:DD:EE:FF)
    pair   AA:BB:CC:DD:EE:FF
    trust  AA:BB:CC:DD:EE:FF
    connect AA:BB:CC:DD:EE:FF
    exit

Once connected (USB plug-in or Bluetooth pairing above), run:
    python3 ps4_test.py

Press R1, R2, L1, L2, and the left/right d-pad arrows. The terminal will print
every button/axis/hat that activates. Use those numbers to verify (or correct)
the MAPPINGS["ps4"] entry in tank.py.

Expected defaults in tank.py:
    R2          -> Axis 5     (trigger, goes from -1.0 to 1.0)
    L2          -> Axis 4
    R1          -> Button 5
    L1          -> Button 4
    D-pad       -> Hat 0  (x=-1 left, x=1 right)
"""

import pygame, time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found.")
    print("Plug the DualShock 4 in via USB, or pair it over Bluetooth (see instructions at top of this file), then try again.")
    raise SystemExit

js = pygame.joystick.Joystick(0)
js.init()
print(f"Connected: {js.get_name()}")
print(f"Buttons: {js.get_numbuttons()}  |  Axes: {js.get_numaxes()}  |  Hats: {js.get_numhats()}")
print("\nPress buttons / triggers / d-pad. Ctrl+C to quit.\n")

try:
    while True:
        pygame.event.pump()
        for i in range(js.get_numbuttons()):
            if js.get_button(i):
                print(f"Button  {i:2d}  pressed")
        for i in range(js.get_numaxes()):
            v = js.get_axis(i)
            if abs(v) > 0.3:
                print(f"Axis    {i:2d}  value: {v:+.2f}")
        for i in range(js.get_numhats()):
            h = js.get_hat(i)
            if h != (0, 0):
                print(f"Hat     {i:2d}  value: {h}  (x=-1 is left, x=1 is right)")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.")
finally:
    pygame.quit()