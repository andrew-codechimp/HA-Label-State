"""Tests for the label_state services."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.label_state.const import DOMAIN
from custom_components.label_state.sensor import SERVICE_RESET

from .test_sensor import LAST_VALUE


async def test_service_reset(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test the post service."""

    sensor_entity_entry = entity_registry.async_get_or_create(
        "sensor", "test_1", "unique", suggested_object_id="test_1"
    )
    assert sensor_entity_entry.entity_id == "sensor.test_1"

    hass.states.async_set("sensor.test_1", str(float(LAST_VALUE)))

    label_state_entity_id = "sensor.my_label_state"

    # Setup the config entry
    config_entry = MockConfigEntry(
        data={},
        domain=DOMAIN,
        options={
            "name": "My periodic min max",
            "entity_id": "sensor.test_1",
            "type": "max",
        },
        title="My label_state",
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert await async_setup_component(hass, DOMAIN, config_entry)
    await hass.async_block_till_done()


    await hass.services.async_call(
        DOMAIN,
        SERVICE_RESET,
        target={"entity_id": label_state_entity_id},
        blocking=True,
        return_response=False,
    )

    state = hass.states.get(label_state_entity_id)

    assert str(float(LAST_VALUE)) == state.state
