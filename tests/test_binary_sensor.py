"""The test for the label_state binary sensor platform."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import label_registry as lr
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from . import setup_integration

VALUES_STATE1 = ["on", "off", "unavailable"]
VALUES_STATE2 = ["on", "off", "unavailable"]
VALUES_NUMERIC = [17, 20, 15.2, 5, 3.8, 9.2, 6.7, 14, 6]
VALUES_ERROR = [17, "string", 15.3]
COUNT = len(VALUES_NUMERIC)
MIN_VALUE = min(VALUES_NUMERIC)
MAX_VALUE = max(VALUES_NUMERIC)
LAST_VALUE = VALUES_NUMERIC[-1]


@pytest.mark.parametrize(
    (
        "state_1",
        "state_2",
        "expected_state",
    ),
    [
        (
            "unavailable",
            "on",
            "on",
        ),
        (
            "on",
            "on",
            "off",
        ),
    ],
)
async def test_state_sensor(
    hass: HomeAssistant,
    state_1: str,
    state_2: str,
    expected_state: str,
    entity_registry: er.EntityRegistry,
    label_registry: lr.LabelRegistry,
) -> None:
    """Test the state sensor."""

    test_label = label_registry.async_create(
        "test",
    )

    sensor1_entity_entry = entity_registry.async_get_or_create(
        "sensor", "test_1", "unique", suggested_object_id="test_1"
    )
    sensor1_entity_entry.labels.add(test_label.label_id)
    assert sensor1_entity_entry.entity_id == "sensor.test_1"

    sensor2_entity_entry = entity_registry.async_get_or_create(
        "sensor", "test_2", "unique", suggested_object_id="test_2"
    )
    sensor2_entity_entry.labels.add(test_label.label_id)
    assert sensor2_entity_entry.entity_id == "sensor.test_2"

    config = MockConfigEntry(
        domain="label_state",
        data={},
        options={
            "name": "test_state",
            "label": test_label.label_id,
            "state_type": "state",
            "state_to": "unavailable",
        },
        title="test_state",
    )

    await setup_integration(hass, config)
    await hass.async_block_till_done()

    hass.states.async_set(sensor1_entity_entry.entity_id, state_1)
    await hass.async_block_till_done()

    hass.states.async_set(sensor2_entity_entry.entity_id, state_2)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.test_state")

    assert state is not None
    assert state.state == expected_state


@pytest.mark.parametrize(
    (
        "state_1",
        "state_2",
        "state_lower_limit",
        "state_upper_limit",
        "expected_state",
    ),
    [
        ("11", "12", "10", "20", "off"),
        ("1", "12", "10", "20", "on"),
    ],
)
async def test_numeric_state_sensor(
    hass: HomeAssistant,
    state_1: str,
    state_2: str,
    state_lower_limit: str,
    state_upper_limit: str,
    expected_state: str,
    entity_registry: er.EntityRegistry,
    label_registry: lr.LabelRegistry,
) -> None:
    """Test the state sensor."""

    test_label = label_registry.async_create(
        "test",
    )

    sensor1_entity_entry = entity_registry.async_get_or_create(
        "sensor", "test_1", "unique", suggested_object_id="test_1"
    )
    sensor1_entity_entry.labels.add(test_label.label_id)
    assert sensor1_entity_entry.entity_id == "sensor.test_1"
    assert test_label.label_id in sensor1_entity_entry.labels

    sensor2_entity_entry = entity_registry.async_get_or_create(
        "sensor", "test_2", "unique", suggested_object_id="test_2"
    )
    sensor2_entity_entry.labels.add(test_label.label_id)
    assert sensor2_entity_entry.entity_id == "sensor.test_2"

    config = MockConfigEntry(
        domain="label_state",
        data={},
        options={
            "name": "test_numeric_state",
            "label": test_label.label_id,
            "state_type": "numeric_state",
            "state_lower_limit": state_lower_limit,
            "state_upper_limit": state_upper_limit,
        },
        title="test_numeric_state",
    )

    config.add_to_hass(hass)
    # await setup_integration(hass, config)
    assert await hass.config_entries.async_setup(config.entry_id)
    await hass.async_block_till_done()

    hass.states.async_set(sensor1_entity_entry.entity_id, state_1)
    await hass.async_block_till_done()

    hass.states.async_set(sensor2_entity_entry.entity_id, state_2)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.test_numeric_state")

    assert state is not None
    assert state.state == expected_state
