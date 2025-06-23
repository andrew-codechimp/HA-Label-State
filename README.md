# HA-Label-State

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Downloads][download-latest-shield]](Downloads)
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

Label State Helpers for Home Assistant

You can create state, not state and numeric state helpers which provide a binary sensor that turns on if any entity with an assigned label matches the criteria you specify.

An `entities` attribute is available which lists all entities that match the criteria.

## Example use cases

- Create a `critical sensors` label and create a State type Label State helper which turns on when any of those entities goes unavailable so you can get a notification.
- Create a `must be on` label and create a Not State type Label State helper which turns on when any of those entities goes to any state but on so you can get a notification.
- If you have appliances which should always draw a certain wattage create a Numeric State type Label State helper to turn on when any of those devices starts drawing 0 watts, triggering a notification.

_Please :star: this repo if you find it useful_  
_If you want to show your support please_

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/codechimp)

![Helper State](https://raw.githubusercontent.com/andrew-codechimp/ha-label-state/main/images/label_state.png "Helper Label State")

![Helper Numeric](https://raw.githubusercontent.com/andrew-codechimp/ha-label-state/main/images/label_state_numeric.png "Helper Label Numeric State")

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrew-codechimp&repository=HA-Label-State&category=Integration)

Restart Home Assistant

In the HA UI go to "Configuration" -> "Devices & services" -> "Helpers" click "+" and select "Label State"

### Manual Installation

<details>
<summary>Show detailed instructions</summary>

Installation via HACS is recommended, but a manual setup is supported.

1. Manually copy custom_components/label_state folder from latest release to custom_components folder in your config folder.
1. Restart Home Assistant.
1. In the HA UI go to "Configuration" -> "Devices & services" -> "Helpers" click "+" and select "Label State"

</details>

## Usage

A new Label State helper will be available within Settings/Helpers or click the My link to jump straight there

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=label_state)

## Tips & FAQ's

Label State can only monitor labels assigned to entities as it needs to know what entity in particular you want to monitor, since devices have many entities that could be switches/values it cannot automatically determine which you want to monitor. It will ignore labels added to anything but an entity.  

Use the example below to create a notification automation listing the entities using the state_attr, replace the binary sensor with your own.  
I like to have the trigger only activate if a labelled sensor has been unavailable for 5 minutes to avoid any planned restarts falsely triggering the automation.

```
alias: Critical Sensors Unavailable
description: "Create a notification if any sensors labelled as critical becomes unavailable for at least 5 minutes"
triggers:
  - trigger: state
    entity_id:
      - binary_sensor.critical_sensor_unavailable
    to: "on"
    for:
      hours: 0
      minutes: 5
      seconds: 0
conditions: []
actions:
  - action: persistent_notification.create
    metadata: {}
    data:
      message: >-
        Critical sensors are unavailable {{
        state_attr('binary_sensor.critical_sensor_unavailable', 'entities') |
        join(', ') }}
mode: single
```

### Translations

You can help by adding missing translations when you are a native speaker. Or add a complete new language when there is no language file available.

Label State uses Crowdin to make contributing easy.

<details>
<summary>Instructions</summary>

**Changing or adding to existing language**

First register and join the translation project

- If you don’t have a Crowdin account yet, create one at [https://crowdin.com](https://crowdin.com)
- Go to the [Label State Crowdin project page](https://crowdin.com/project/label-state)
- Click Join.

Next translate a string

- Select the language you want to contribute to from the dashboard.
- Click Translate All.
- Find the string you want to edit, missing translation are marked red.
- Fill in or modify the translation and click Save.
- Repeat for other translations.

Label State will automatically pull in latest changes to translations every day and create a Pull Request. After that is reviewed by a maintainer it will be included in the next release of Label State.

**Adding a new language**

Create an [Issue](https://github.com/andrew-codechimp/HA-Label-State/issues/) requesting a new language. We will do the necessary work to add the new translation to the integration and Crowdin site, when it's ready for you to contribute we'll comment on the issue you raised.

</details>

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/andrew-codechimp/HA-Label-State.svg?style=for-the-badge
[commits]: https://github.com/andrew-codechimp/HA-Label-State/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[exampleimg]: example.png
[license-shield]: https://img.shields.io/github/license/andrew-codechimp/HA-Label-State.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/andrew-codechimp/HA-Label-State.svg?style=for-the-badge
[releases]: https://github.com/andrew-codechimp/HA-Label-State/releases
[download-latest-shield]: https://img.shields.io/github/downloads/andrew-codechimp/HA-Label-State/latest/total?style=for-the-badge
