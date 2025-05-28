"""Binary sensor platform for label_state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
    AddEntitiesCallback,
)
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    ATTR_ENTITIES,
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    LOGGER,
    StateTypes,
)


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize label state config entry."""

    name: str | None = config_entry.options.get(CONF_NAME)
    label: str = config_entry.options[CONF_LABEL]
    state_type: str = config_entry.options[CONF_STATE_TYPE]
    state_to: str | None = config_entry.options.get(CONF_STATE_TO)
    state_lower_limit: float | None = config_entry.options.get(CONF_STATE_LOWER_LIMIT)
    state_upper_limit: float | None = config_entry.options.get(CONF_STATE_UPPER_LIMIT)
    unique_id = config_entry.entry_id

    config_entry.async_on_unload(
        config_entry.add_update_listener(config_entry_update_listener)
    )

    async_add_entities(
        [
            LabelStateBinarySensor(
                hass,
                label,
                name,
                state_type,
                state_to,
                state_lower_limit,
                state_upper_limit,
                unique_id,
            )
        ]
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the min/max/mean sensor."""
    label: str = config[CONF_LABEL]
    name: str | None = config.get(CONF_NAME)
    state_type: str = config[CONF_STATE_TYPE]
    state_to: str | None = config.get(CONF_STATE_TO)
    state_lower_limit: float | None = config.get(CONF_STATE_LOWER_LIMIT)
    state_upper_limit: float | None = config.get(CONF_STATE_UPPER_LIMIT)
    unique_id = config.get(CONF_UNIQUE_ID)

    async_add_entities(
        [
            LabelStateBinarySensor(
                hass,
                label,
                name,
                state_type,
                state_to,
                state_lower_limit,
                state_upper_limit,
                unique_id,
            )
        ]
    )


class LabelStateBinarySensor(BinarySensorEntity):
    """Representation of a Label State sensor."""

    _attr_icon = "mdi:tag"
    _attr_should_poll = False

    _state_dict: dict[str, str] = {}

    def __init__(
        self,
        hass: HomeAssistant,
        label: str,
        name: str | None,
        state_type: str,
        state_to: str | None,
        state_lower_limit: float | None,
        state_upper_limit: float | None,
        unique_id: str | None,
    ) -> None:
        """Initialize the label state sensor."""
        self._attr_unique_id = unique_id
        self._label = label
        self._state_type = state_type
        self._state_to = state_to
        self._state_lower_limit = state_lower_limit
        self._state_upper_limit = state_upper_limit
        self._attr_name = name

        self._unit_of_measurement_mismatch = False

        self._attr_is_on = False
        self._attr_extra_state_attributes = {}
        self._attr_extra_state_attributes.update(
            {
                ATTR_ENTITIES: [],
            }
        )

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""

        await super().async_added_to_hass()

        ent_reg = er.async_get(self.hass)
        entries = er.async_entries_for_label(ent_reg, self._label)

        for entity_entry in entries:
            for label in entity_entry.labels:
                if label == self._label:
                    LOGGER.debug(
                        "Found label %s in entity %s",
                        self._label,
                        entity_entry.entity_id,
                    )

                    # Replay current state of the labelled entitiy
                    state = self.hass.states.get(entity_entry.entity_id)
                    state_event: Event[EventStateChangedData] = Event(
                        "",
                        {
                            "entity_id": entity_entry.entity_id,
                            "new_state": state,
                            "old_state": None,
                        },
                    )

                    if entity_entry and self._label in entity_entry.labels:
                        self._async_state_listener(state_event, update_state=False)

                    self.async_on_remove(
                        async_track_state_change_event(
                            self.hass,
                            entity_entry.entity_id,
                            self._async_state_listener,
                        )
                    )

        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_ENTITY_REGISTRY_UPDATED,
                self._async_entity_registry_modified,
            )
        )

        self._calc_state()
        self.async_write_ha_state()

    @callback
    def _async_entity_registry_modified(
        self, event: Event[er.EventEntityRegistryUpdatedData]
    ) -> None:
        """Handle entity registry update."""
        data = event.data
        if data["action"] == "update" and data["changes"].get("labels") is not None:
            # Get the entity, check it's current labels
            entity_registry = er.async_get(self.hass)
            entity_entry = entity_registry.async_get(data["entity_id"])
            if entity_entry and self._label in entity_entry.labels:
                # The entity has a label, ensure we listen to it
                self.async_on_remove(
                    async_track_state_change_event(
                        self.hass,
                        entity_entry.entity_id,
                        self._async_state_listener,
                    )
                )
                LOGGER.debug(
                    "Found label %s in entity %s",
                    self._label,
                    entity_entry.entity_id,
                )

            self._calc_state()
            self.async_write_ha_state()

    @callback
    def _async_state_listener(
        self, event: Event[EventStateChangedData], update_state: bool = True
    ) -> None:
        """Handle the sensor state changes."""
        entity_id = event.data["entity_id"]
        new_state = event.data["new_state"]

        LOGGER.debug("State changed for %s", entity_id)

        # Store the state string in a dictionary keyed by the entity_id
        self._state_dict[entity_id] = (
            new_state.state if new_state is not None else STATE_UNKNOWN
        )

        self._calc_state()

        if update_state:
            self.async_write_ha_state()

    @callback
    def _calc_state(self) -> None:
        """Calculate the state."""

        state_is_on: bool | None = False
        entities_on: list[str] = []

        entity_registry = er.async_get(self.hass)

        if self._state_type == StateTypes.STATE:
            for entity_id in self._state_dict.keys():
                # Check if the state still has the label
                entity_entry = entity_registry.async_get(entity_id)
                if entity_entry and self._label in entity_entry.labels:
                    entity_state = self._state_dict[entity_id]

                    if (
                        entity_state
                        and self._state_to
                        and entity_state.casefold() == self._state_to.casefold()
                    ):
                        state_is_on = True
                        entities_on.append(entity_id)

        if self._state_type == StateTypes.NUMERIC_STATE:
            for entity_id in self._state_dict.keys():
                # Check if the state still has the label
                entity_entry = entity_registry.async_get(entity_id)
                if entity_entry and self._label in entity_entry.labels:
                    entity_state = self._state_dict[entity_id]

                    try:
                        if (
                            entity_state
                            and entity_state != STATE_UNKNOWN
                            and entity_state != STATE_UNAVAILABLE
                            and self._state_lower_limit is not None
                            and self._state_upper_limit is not None
                        ):
                            if (
                                float(entity_state) < self._state_lower_limit
                                or float(entity_state) > self._state_upper_limit
                            ):
                                state_is_on = True
                                entities_on.append(entity_id)
                                LOGGER.debug(
                                    "State %s is below lower limit %s and above upper limit %s for %s",
                                    entity_state,
                                    self._state_lower_limit,
                                    self._state_upper_limit,
                                    entity_id,
                                )
                        else:
                            if (
                                entity_state
                                and entity_state != STATE_UNKNOWN
                                and entity_state != STATE_UNAVAILABLE
                                and self._state_lower_limit
                                and float(entity_state) < self._state_lower_limit
                            ):
                                state_is_on = True
                                entities_on.append(entity_id)
                                LOGGER.debug(
                                    "State %s is below lower limit %s for %s",
                                    entity_state,
                                    self._state_lower_limit,
                                    entity_id,
                                )

                            if (
                                entity_state
                                and entity_state != STATE_UNKNOWN
                                and entity_state != STATE_UNAVAILABLE
                                and self._state_upper_limit
                                and float(entity_state) > self._state_upper_limit
                            ):
                                state_is_on = True
                                entities_on.append(entity_id)
                                LOGGER.debug(
                                    "State %s is above upper limit %s for %s",
                                    entity_state,
                                    self._state_upper_limit,
                                    entity_id,
                                )

                    except ValueError:
                        LOGGER.error(
                            "Unable to determine state. Only numerical states are supported"
                        )
                        state_is_on = None

        LOGGER.debug(
            "State is %s for %s",
            state_is_on,
            self.entity_id,
        )

        self._attr_is_on = state_is_on
        self._attr_extra_state_attributes[ATTR_ENTITIES] = entities_on
