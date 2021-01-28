# Hilo
Hilo integration for Home Assistant

# What This Is:
This is a custom component to allow control of Hilo devices.

# What It Does:
- Get current temperature of thermostat
- Update target temperature of thermostat
- Get power of energy meter

# To Do:
- Get power of each devices
- Add functionnalities for other devices

# How To Setup:
Copy the hilo directory from the latest release to your customer_components directory.

After copying all files from the hilo directory, your configuration should look like:
```
hilo:
  username: YourHiloUsername
  password: YourHiloPassword
```
