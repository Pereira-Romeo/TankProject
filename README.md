# Tank Project

#### Table of contents

1. **[Objectif](#objectif)**
2. **[Project's Team](#team)**
3. **[Additional documentation](#documentation)**
4. **[Installing as a service](#installing-as-a-service)**
5. **[Dependencies](#dependencies)**

## Objectif

This project aims to design and build a 3D printed mini-tank on tracks, powered by two electric motors.

It is part of a practical learning approach combining:

- 3D design;
- the on-board electronics;
- the programming.

The final objective is to obtain a functional mobile vehicle intended for demonstrations and experimentation.

## Team

- Dorian
- Mewen
- Ronan
- Roméo

## Documentation

- **[About the tank's models and scripts](./doc/about_tank.md)**
- **[About the tank's Components and wiring](./doc/about_wiring.md)**


## Installing as a service

You can simply run `sudo ./install_service.sh` in your shell.

> [!NOTE]
> This install script needs to run as root because it can:
> 1. create a user
> 2. write in protected directories (`/etc/systemd/system/`)

This install script will do the following:
1. Create user "pi" (and it's home folder + add it to necessary groups)
2. Install dependencies (which you can see in the next section)
3. Setup pi's folder and files for the tank
4. Install the service
5. Start the service

## Dependencies

- **[python3](https://www.python.org/)**
- **[pygame](https://www.pygame.org/wiki/about)**
- **[gpiozero](https://gpiozero.readthedocs.io/en/stable/)**

If you already have python installed, you can install the dependencies with the following command:

```sh
pip3 install -r requirements.txt --break-system-packages
```

> [!NOTE]
> The `--break-system-packages` flag is necessary on Raspberry Pi OS.
