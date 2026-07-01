#!/usr/bin/env python3
"""
Tank vehicle controller — Raspberry Pi 4 + L298N motor driver.

Supported controllers (auto-detected):
    PS3  DualShock 3       USB
    PS4  DualShock 4       Bluetooth
    PS5  DualSense         Bluetooth
    Xbox One / Series X/S  Bluetooth

Drive controls (same across all controllers):
    R2 / RT  = right motor forward
    R1 / RB  = right motor backward
    L2 / LT  = left motor forward
    L1 / LB  = left motor backward

Turret controls (same across all controllers):
    D-pad LEFT  = turret rotate left
    D-pad RIGHT = turret rotate right

Safety: pressing both directions of any motor at once stops that motor.

GPIO pin assignment (BCM numbering):
    RIGHT_FORWARD_PIN  = 17   ->  L298N IN1   (right motor)
    RIGHT_BACKWARD_PIN = 27   ->  L298N IN2   (right motor)
    LEFT_FORWARD_PIN   = 22   ->  L298N IN3   (left motor)
    LEFT_BACKWARD_PIN  = 23   ->  L298N IN4   (left motor)
    TURRET_LEFT_PIN    = 24   ->  L298N IN1   (turret, second L298N channel or board)
    TURRET_RIGHT_PIN   = 25   ->  L298N IN2   (turret)
"""

import signal
import time
import pygame
from gpiozero import OutputDevice

# ---------------------------------------------------------------------------
# GPIO PIN CONFIG -- edit here if your wiring differs
# ---------------------------------------------------------------------------
RIGHT_FORWARD_PIN = 23
RIGHT_BACKWARD_PIN = 24
LEFT_FORWARD_PIN = 27
LEFT_BACKWARD_PIN = 17
TURRET_LEFT_PIN = 5
TURRET_RIGHT_PIN = 6

# Triggers rest at -1.0 (released) and go up to 1.0 (fully pressed).
# We treat anything above this threshold as "pressed".
TRIGGER_THRESHOLD = 0.0

# ---------------------------------------------------------------------------
# CONTROLLER MAPPINGS
# Each mapping has:
#   trig_*       : axis index for analog triggers (R2/L2 or RT/LT)
#   btn_*        : button index for shoulder buttons (R1/L1 or RB/LB)
#   dpad_type    : "hat"    -> d-pad is a hat (get_hat)
#                  "button" -> d-pad is 4 individual buttons
#                  "axis"   -> d-pad is an axis pair
#   dpad_hat     : hat index (when dpad_type == "hat")
#   dpad_left/right_btn : button indices (when dpad_type == "button")
#   dpad_axis    : axis index for horizontal d-pad (when dpad_type == "axis")
# ---------------------------------------------------------------------------
MAPPINGS = {
    "ps3": {
        "trig_right":        5,   # R2 axis
        "trig_left":         2,   # L2 axis
        "btn_right_back":    5,   # R1
        "btn_left_back":     4,   # L1
        "dpad_type":         "button",
        "dpad_left_btn":     15,
        "dpad_right_btn":    16,   # NOTE: will be confirmed by controller_test
    },
    "ps4": {
        "trig_right":        5,   # R2 axis
        "trig_left":         2,   # L2 axis
        "btn_right_back":    5,   # R1
        "btn_left_back":     4,   # L1
        "dpad_type":         "hat",
        "dpad_hat":          0,
    },
    "ps5": {
        "trig_right":        5,   # R2 axis
        "trig_left":         4,   # L2 axis
        "btn_right_back":    7,   # R1
        "btn_left_back":     6,   # L1
        "dpad_type":         "hat",
        "dpad_hat":          0,
    },
    "xbox": {
        "trig_right":        5,   # RT axis
        "trig_left":         2,   # LT axis
        "btn_right_back":    5,   # RB
        "btn_left_back":     4,   # LB
        "dpad_type":         "hat",
        "dpad_hat":          0,
    },
}

# Substrings used to detect controller type from joystick name (lowercase)
CONTROLLER_HINTS = {
    "ps3":  ["playstation(r)3", "ps3", "sixaxis", "dualshock 3"],
    "ps4":  ["wireless controller", "ps4", "dualshock 4"],
    "ps5":  ["dualsense", "ps5", "dualshock 5", "playstation 5"],
    "xbox": ["xbox", "x-box", "xinput", "microsoft"],
}

# ---------------------------------------------------------------------------
# GPIO SETUP
# ---------------------------------------------------------------------------
right_forward  = OutputDevice(RIGHT_FORWARD_PIN)
right_backward = OutputDevice(RIGHT_BACKWARD_PIN)
left_forward   = OutputDevice(LEFT_FORWARD_PIN)
left_backward  = OutputDevice(LEFT_BACKWARD_PIN)
turret_left    = OutputDevice(TURRET_LEFT_PIN)
turret_right   = OutputDevice(TURRET_RIGHT_PIN)


def set_motor(fwd_pin, bwd_pin, forward_pressed, backward_pressed):
    """Generic motor driver: forward, backward, stop, or safety-stop."""
    if forward_pressed and backward_pressed:
        fwd_pin.off(); bwd_pin.off()
    elif forward_pressed:
        fwd_pin.on();  bwd_pin.off()
    elif backward_pressed:
        fwd_pin.off(); bwd_pin.on()
    else:
        fwd_pin.off(); bwd_pin.off()


def stop_all():
    for pin in (right_forward, right_backward,
                left_forward,  left_backward,
                turret_left,   turret_right):
        pin.off()


# ---------------------------------------------------------------------------
# CONTROLLER DETECTION
# ---------------------------------------------------------------------------
def detect_type(name):
    lowered = name.lower()
    for ctype, hints in CONTROLLER_HINTS.items():
        if any(h in lowered for h in hints):
            return ctype
    return None


def read_dpad(joystick, mapping):
    """
    Returns (left_pressed, right_pressed) regardless of whether the d-pad
    is implemented as a hat, a button pair, or an axis.
    """
    dtype = mapping["dpad_type"]

    if dtype == "hat":
        hat = joystick.get_hat(mapping["dpad_hat"])
        # hat is (x, y): x=-1 left, x=1 right
        return hat[0] == -1, hat[0] == 1

    elif dtype == "button":
        left  = joystick.get_button(mapping["dpad_left_btn"]) == 1
        right = joystick.get_button(mapping["dpad_right_btn"]) == 1
        return left, right

    elif dtype == "axis":
        val = joystick.get_axis(mapping["dpad_axis"])
        return val < -0.5, val > 0.5

    return False, False


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def wait_for_controller():
    """Block until at least one joystick is connected, then return it."""
    printed = False
    while True:
        pygame.joystick.quit()   # re-init forces pygame to re-scan USB/BT devices
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            return joystick
        if not printed:
            print("Waiting for controller...")
            print("  PS3  -> plug in via USB")
            print("  PS4  -> pair via Bluetooth")
            print("  PS5  -> pair via Bluetooth")
            print("  Xbox -> pair via Bluetooth")
            printed = True
        time.sleep(1)


def main():
    # Make SIGTERM (sent by systemctl stop) behave like Ctrl+C so the
    # finally block runs and motors are stopped before the process exits.
    signal.signal(signal.SIGTERM, lambda signum, frame: (_ for _ in ()).throw(KeyboardInterrupt()))

    pygame.init()
    pygame.joystick.init()

    try:
        while True:
            # --- wait until a controller appears ---
            joystick = wait_for_controller()
            name = joystick.get_name()
            print(f"Controller connected: {name}")

            ctype = detect_type(name)
            if ctype is None:
                print("Warning: could not auto-detect controller type -- defaulting to PS3 mapping.")
                print("If controls feel wrong, run the appropriate *_test.py script to find your")
                print("button/axis numbers and update MAPPINGS at the top of tank.py.")
                ctype = "ps3"
            else:
                print(f"Detected: {ctype.upper()}")

            mapping = MAPPINGS[ctype]
            print("Running. Ctrl+C to stop.\n")

            # --- drive loop: runs until controller disconnects or Ctrl+C ---
            try:
                while True:
                    pygame.event.pump()

                    # detect disconnect: pygame reports 0 joysticks when one is lost
                    if pygame.joystick.get_count() == 0:
                        print("Controller disconnected -- motors stopped, waiting for reconnect...")
                        stop_all()
                        break  # back to wait_for_controller()

                    # --- drive motors ---
                    fwd_right  = joystick.get_axis(mapping["trig_right"]) > TRIGGER_THRESHOLD
                    fwd_left   = joystick.get_axis(mapping["trig_left"])  > TRIGGER_THRESHOLD
                    bwd_right  = joystick.get_button(mapping["btn_right_back"]) == 1
                    bwd_left   = joystick.get_button(mapping["btn_left_back"])  == 1

                    set_motor(right_forward, right_backward, fwd_right, bwd_right)
                    set_motor(left_forward,  left_backward,  fwd_left,  bwd_left)

                    # --- turret motor ---
                    t_left, t_right = read_dpad(joystick, mapping)
                    set_motor(turret_left, turret_right, t_left, t_right)

                    time.sleep(0.05)  # ~20 Hz

            except pygame.error:
                # pygame throws this if the joystick disappears mid-read
                print("Controller lost -- motors stopped, waiting for reconnect...")
                stop_all()
                # loop continues back to wait_for_controller()

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stop_all()
        pygame.quit()


if __name__ == "__main__":
    main()
