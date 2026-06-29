#!/usr/bin/env python3
"""
PS3 controller (USB) diagnostic tool.

Plug the PS3 controller in via USB, then run:
    python3 ps3_test.py

Press R1, R2, L1, L2, and the left/right d-pad arrows. The terminal will print
the index of every button/axis/hat that moves. Use those numbers to verify (or
correct) the MAPPINGS["ps3"] entry in tank.py.

Expected defaults in tank.py:
    R2          -> Axis 5     (trigger, goes from -1.0 to 1.0)
    L2          -> Axis 2
    R1          -> Button 5
    L1          -> Button 4
    D-pad left  -> Button 7   (PS3 d-pad is usually buttons, not a hat)
    D-pad right -> Button 5   (check yours -- it varies by driver)
"""

import pygame, time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found. Plug the PS3 controller in via USB and try again.")
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
                print(f"Hat     {i:2d}  value: {h}")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.")
finally:
    pygame.quit()
