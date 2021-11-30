[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Hilo
[Hilo](https://www.hydroquebec.com/hilo/en/) integration for Home Assistant

## Introduction

This is a custom component to allow control of Hilo devices from Home Assistant. This is an unofficial integration and unsupported
by Hilo.

We are not employees of, or paid by, Hilo. We can't be held responsible if your account is getting suspended because of the use of
this integration. Hilo might change their API any time and this might break this integration.

### Features
- Support for switches and dimmers as light devices
- Get current and set target temperature of thermostat
- Get energy usage of pretty much each devices
- Generates energy meters and sensors
- Binary sensor for Hilo Events (challenges)
- Binary sensor for Hilo Gateway

### To Do:
- Add functionnalities for other devices
- unit and functional tests
- [Adding type hints to the code](https://developers.home-assistant.io/docs/development_typing/)
- Write a separate library for the hilo api mapping

## Installation

### Manual

Copy the `custom_components/hilo` directory from the latest release to your `customer_components` directory.

### HACS

Follow standard HACS procedure to install.

## Configuration

To function properly, we need to include the Hilo credentials in the `configuration.yaml` file like this:
```
hilo:
  username: YourHiloUsername
  password: YourHiloPassword
```

### Advanced configuration
- `light_as_switch`: Boolean
  Will add light entities as switch entities. This was the default behavior of the integration and this is to
  give users the option to stay with that behavior instead of having to rewrite all their automations and scripts.
  The current default behavior is to add light entities as light entities.

- `generate_energy_meters`: Boolean (beta)
  Will generate all the entities and sensors required to feed the `Energy` dashboard.
  For details, see the [note below](#energy-meters).

- `hq_plan_name`: String
  Define the Hydro Quebec rate plan name.
  Only 2 values are supported at this time:
  - `rate d`
  - `flex d`

- `scan_interval`: Integer
  Number of seconds between each device update. Defaults to 60 and it's not recommended to go below 30 as it might
  result in a suspension from Hilo.

### Sample complete configuration

```
utility_meter:
hilo:
  username: !secret hilo_username
  password: !secret hilo_password
  generate_energy_meters: true
  hq_plan_name: rate d
  scan_interval: 30
```

## Energy meters
Energy meters are a new feature of this integration. We used to manually generate them with template sensors and automation
but they now have been fully integrated into the Hilo integration.

All generated entities and sensors will be prefixed with `hilo_energy_` or `hilo_rate_`.

### How to enable them

* Add `generate_energy_meters` to your `hilo` configuration block in `configuration.yaml` and set it to `true` like in the
  sample config above.

* If you never configured any utility meter, you will need to add an empty `utility_meter` block in your `configuration.yaml`.
  The reason why we do this is because there's no official API to integrate the meters.

* Restart home assistant and wait 5 minutes until you see the `sensor.hilo_energy_total_low` entity gettin created and populated
  with data:
  * The `status` should be in `collecting`
  * The `state` should be a number higher than 0.

* Once the data is starting to get populated, restart home assistant again. Not sure why this is necessary but without that, the
  energy dashboard doesn't show the collected sensors.

* If you see the following error in your logs, just wait for 5 minutes and restart home assistant again. The integration should
  heal itself:

    ```
    2021-11-29 22:03:46 ERROR (MainThread) [homeassistant] Error doing job: Task exception was never retrieved
    Traceback (most recent call last):
    [...]
    ValueError: could not convert string to float: 'None'
    ```

* If you still see these errors, don't worry too much. This means that the meters don't have any data in them. These errors will
  vanish when the meters will get some data. So turn on your thermostats, your lights and everything.

### Lovelace sample integration

Here's an example on how to add the energy data to Lovelace:
```
      - type: vertical-stack
        cards:
          - type: horizontal-stack
            cards:
              - type: entity
                entity: binary_sensor.defi_hilo
                icon: mdi:fire
              - type: entity
                entity: sensor.smartenergymeter
                name: Hydro
                icon: mdi:speedometer
              - type: entity
                entity: sensor.hilo_rate_current
                name: Cout Actuel
          - type: energy-date-selection
          - type: energy-sources-table
          - type: energy-usage-graph
          - type: energy-distribution
            link_dashboard: true
```


### Warning

When enabling Hilo generated energy meters, it's recommended to remove the manually generated ones to have the most accurate
statistics, otherwise we might end up with duplicate data.

This wasn't tested with already active data and energy entities (ie: Battery, Gaz, Solar, or even other individual devices).
It's possible that enabling this will break or delete these original sensors. We can't be held responsible for any data loss
service downtime, or any kind as it's described in the license.

If you're facing an issue and you want to collaborate, please enable `debug` log level for this integration and provide a copy
of the `home-assistant.log` file. Details on how to enable `debug` are below.

## References

As stated above, this is an unofficial integration. Hilo is not supporting direct API calls and might obfuscate the service or
prevent us from using it.

For now, these are the swagger links we've found:
* https://wapphqcdev01-automation.azurewebsites.net/swagger/index.html
* https://wapphqcdev01-notification.azurewebsites.net/swagger/index.html
* https://wapphqcdev01-clientele.azurewebsites.net/swagger/index.html


# Contributing

Reporting any kind of issue is a good way of contributing to the project and it's available to anyone.

If you face any kind of problem or weird behavior, please submit an issue and ideal, attach debug logs.

To enable debug log level, you need to add this to your `configuration.yaml` file:
```
logger:
  default: info
  logs:
     custom_components.hilo: debug
```

If you have any kind of python/home-assistant experience and want to contribute to the code, feel free to submit a merge request.

## Collaborators

* [Francis Poisson](https://github.com/francispoisson/)
* [David Vallee Delisle](https://github.com/valleedelisle/)
