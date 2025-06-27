"""Support for label_state event entities."""

from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, EVENT_LABEL_STATE_UPDATED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Label State event."""

    async_add_entities([LabelStateEventEntity(entry)])


class LabelStateEventEntity(EventEntity):
    """Representation of a Label State event entity."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_event_types = [EVENT_LABEL_STATE_UPDATED]
    _attr_name = None
    _attr_translation_key = DOMAIN

    def __init__(
        self,
        entry: ConfigEntry,
    ) -> None:
        """Initialise a Label State event entity."""
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Label State",
        )
        self._attr_unique_id = entry.entry_id
        self._entry = entry

    @callback
    def _async_handle_event(self, event: str, _extra: dict[str, Any]) -> None:
        """Handle the event."""
        self._trigger_event(event, _extra)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        signal = f"{DOMAIN}-{self._entry.entry_id}"
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal, self._async_handle_event)
        )
