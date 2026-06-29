#!/usr/bin/env python3
"""
Xbox controller (Bluetooth) diagnostic tool.

--- Pairing the Xbox controller via Bluetooth ---

    bluetoothctl
    power on
    agent on
    scan on
    # Hold the Xbox button, then hold the small pair button on top until it flashes fast
    # When it appears in the scan list, note its MAC (e.g. AA:BB:CC:DD:EE:FF)
    pair   AA:BB:CC:DD:EE:FF
    trust  AA:BB:CC:DD:EE:FF
    connect AA:BB:CC:DD:EE:FF
    exit

Once connected, run:
    python3 xbox_test.py

Press RB, RT, LB, LT, and the left/right d-pad. The terminal will print every
button/axis/hat that activates. Use those to verify (or correct) the
MAPPINGS["xbox"] entry in tank.py.

Expected defaults in tank.py:
    RT          -> Axis 5     (rests at -1.0, goes to 1.0 when pressed)
    LT          -> Axis 2
    RB          -> Button 5
    LB          -> Button 4
    D-pad       -> Hat 0  (x=-1 left, x=1 right)
"""

import pygame, time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found.")
    print("Pair the Xbox controller over Bluetooth (see instructions at top of this file) then try again.")
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
