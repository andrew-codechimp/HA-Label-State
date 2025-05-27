"""Test label_state setup process."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import label_registry as lr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.label_state.const import DOMAIN

from .const import DEFAULT_NAME


async def test_unload_entry(hass: HomeAssistant, loaded_entry: MockConfigEntry) -> None:
    """Test unload an entry."""

    assert loaded_entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(loaded_entry.entry_id)
    await hass.async_block_till_done()
    assert loaded_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    label_registry: lr.LabelRegistry,
) -> None:
    """Test the setup of the helper PeriodicMinMax."""

    # Source entity device config entry
    source_config_entry = MockConfigEntry()
    source_config_entry.add_to_hass(hass)

    # Device entry of the source entity
    source_device_entry = device_registry.async_get_or_create(
        config_entry_id=source_config_entry.entry_id,
        identifiers={("sensor", "test_source")},
    )

    test_label = label_registry.async_create(
        "test",
    )

    # Source entity registry
    source_entity = entity_registry.async_get_or_create(
        "sensor",
        "test",
        "source",
        config_entry=source_config_entry,
        device_id=source_device_entry.id,
    )
    source_entity.labels.add(test_label.label_id)

    await hass.async_block_till_done()
    assert entity_registry.async_get("sensor.test_source") is not None

    # Configure the configuration entry for PeriodicMinMax
    label_state_config_entry = MockConfigEntry(
        data={},
        domain=DOMAIN,
        options={
            "name": DEFAULT_NAME,
            "label": test_label.label_id,
            "state_type": "state",
            "state_to": "on",
        },
        title=DEFAULT_NAME,
    )
    label_state_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(label_state_config_entry.entry_id)
    await hass.async_block_till_done()

    # Config entry reload
    await hass.config_entries.async_reload(label_state_config_entry.entry_id)
    await hass.async_block_till_done()

    # Remove the config entry
    assert await hass.config_entries.async_remove(label_state_config_entry.entry_id)
    await hass.async_block_till_done()
