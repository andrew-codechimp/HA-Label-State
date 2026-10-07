"""Tests for Label State setup, options reload, and cleanup."""

import pytest
from custom_components.label_state.const import CONF_LABEL, CONF_STATE_TO
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration
from .const import ENTITY_ID, SOURCE_ENTITY_ID

pytestmark = pytest.mark.usefixtures("labeled_sources")


async def test_setup_remove(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test one helper entity is created and removal clears its state and registry entry."""
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED
    entities = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    assert len(entities) == 1
    assert entities[0].entity_id == ENTITY_ID
    assert entities[0].unique_id == mock_config_entry.entry_id
    assert await hass.config_entries.async_remove(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID) is None
    assert entity_registry.async_get(ENTITY_ID) is None
    assert entity_registry.async_get(SOURCE_ENTITY_ID) is not None


async def test_unload(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test unloading unsubscribes both source and registry listeners."""
    await setup_integration(hass, mock_config_entry)
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    previous = hass.states.get(ENTITY_ID)
    assert previous.state == "unavailable"
    hass.states.async_set(SOURCE_ENTITY_ID, "on")
    entity_registry.async_update_entity(SOURCE_ENTITY_ID, labels=set())
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID) == previous


async def test_options_reload(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test saving options reloads the helper and applies the new matching state."""
    await setup_integration(hass, mock_config_entry)
    assert hass.states.get(ENTITY_ID).state == "off"
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_LABEL: "test", CONF_STATE_TO: "off"}
    )
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert hass.states.get(ENTITY_ID).state == "on"
