# Bluetooth pairing tool



## Table of contents

1. **[Automatic pairing](#automatic-pairing)**
2. **[Manual pairing](#manual-pairing)**
2. **[you controller's pairing mode](#making-your-controller-enter-pairing-mode)**

[readme backlink](../README.md) \
[tank controls backlink](./about_tank.md#controls)

# Automatic pairing

> [!WARNING]
> Make sure the only controller in pairing mode in the vicinity is your controller, the script cannot guess YOUR controller and will take the first one it sees

From the repo's root, run one of the following depending on your controller:
```sh
./diagnosis_tools/bt_controller_pairing_tool.py --ps4
./diagnosis_tools/bt_controller_pairing_tool.py --ps5
./diagnosis_tools/bt_controller_pairing_tool.py --xbox
```

# Manual pairing

Find your controller's mac address (`AA:BB:CC:DD:EE:FF` here) then on the raspberry run:
bluetoothctl
pair   AA:BB:CC:DD:EE:FF
trust  AA:BB:CC:DD:EE:FF
connect AA:BB:CC:DD:EE:FF
exit (or ctrl + D)

# Making your controller enter pairing mode

## ps4/ps5
Hold the ps button and the share button, \
once the light flashes fast you are in pairing mode, \
hold until you are done pairing

## Xbox
hold Xbox button, then hold small pair button until it flashes fast

