"""Tests for labeled state matching and label/entity registry changes."""

from unittest.mock import Mock

import pytest
from custom_components.label_state.binary_sensor import (
    LabelStateBinarySensor,
    async_setup_platform,
)
from custom_components.label_state.const import (
    ATTR_ENTITIES,
    ATTR_ENTITY_NAMES,
    ATTR_LABEL_NAME,
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_NOT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    StateTypes,
)
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    snapshot_platform,
)
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    label_registry as lr,
)

from . import setup_integration
from .const import ENTITY_ID, OTHER_ENTITY_ID, SOURCE_ENTITY_ID

pytestmark = pytest.mark.usefixtures("labeled_sources")


async def test_entity(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test entity metadata and the names of currently matching sources."""
    hass.states.async_set(SOURCE_ENTITY_ID, "on")
    await setup_integration(hass, mock_config_entry)
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    ("mock_config_entry", "value", "expected", "matches"),
    [
        pytest.param(
            {CONF_STATE_TO: "ON"}, "on", "on", [SOURCE_ENTITY_ID], id="casefold-match"
        ),
        pytest.param({}, "off", "off", [], id="no-match"),
        pytest.param(
            {CONF_STATE_TO: "unavailable"},
            "unavailable",
            "on",
            [SOURCE_ENTITY_ID],
            id="unavailable-match",
        ),
        pytest.param(
            {CONF_STATE_TO: "unknown"},
            "unknown",
            "on",
            [SOURCE_ENTITY_ID],
            id="unknown-match",
        ),
        pytest.param(
            {CONF_STATE_TYPE: StateTypes.NOT_STATE, CONF_STATE_NOT: "OFF"},
            "on",
            "on",
            [SOURCE_ENTITY_ID],
            id="not-state-casefold",
        ),
        pytest.param(
            {CONF_STATE_TYPE: StateTypes.NOT_STATE, CONF_STATE_NOT: "off"},
            "off",
            "off",
            [],
            id="not-state-miss",
        ),
        pytest.param(
            {CONF_STATE_TYPE: StateTypes.NOT_STATE, CONF_STATE_NOT: "off"},
            "unavailable",
            "on",
            [SOURCE_ENTITY_ID],
            id="not-state-unavailable",
        ),
    ],
    indirect=["mock_config_entry"],
)
async def test_state_matching(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    value: str,
    expected: str,
    matches: list[str],
) -> None:
    """Test exact state and inverse state matching, including special source states."""
    await setup_integration(hass, mock_config_entry)
    hass.states.async_set(SOURCE_ENTITY_ID, value)
    await hass.async_block_till_done()
    state = hass.states.get(ENTITY_ID)
    assert state.state == expected
    assert state.attributes[ATTR_ENTITIES] == matches
    assert state.attributes[ATTR_ENTITY_NAMES] == ["Source"][: len(matches)]


@pytest.mark.parametrize(
    ("limits", "value", "expected"),
    [
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10, CONF_STATE_UPPER_LIMIT: 90},
            "9",
            "on",
            id="below-range",
        ),
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10, CONF_STATE_UPPER_LIMIT: 90},
            "10",
            "off",
            id="lower-inclusive",
        ),
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10, CONF_STATE_UPPER_LIMIT: 90},
            "90",
            "off",
            id="upper-inclusive",
        ),
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10, CONF_STATE_UPPER_LIMIT: 90},
            "91",
            "on",
            id="above-range",
        ),
        pytest.param({CONF_STATE_LOWER_LIMIT: 10}, "9", "on", id="lower-only"),
        pytest.param({CONF_STATE_LOWER_LIMIT: 10}, "11", "off", id="lower-only-miss"),
        pytest.param({CONF_STATE_UPPER_LIMIT: 90}, "91", "on", id="upper-only"),
        pytest.param({CONF_STATE_UPPER_LIMIT: 90}, "89", "off", id="upper-only-miss"),
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10}, "invalid", "unknown", id="non-numeric"
        ),
        pytest.param({CONF_STATE_LOWER_LIMIT: 10}, "unknown", "off", id="unknown"),
        pytest.param(
            {CONF_STATE_LOWER_LIMIT: 10}, "unavailable", "off", id="unavailable"
        ),
    ],
)
async def test_numeric_matching(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    limits: dict[str, float],
    value: str,
    expected: str,
) -> None:
    """Test numeric matching outside inclusive limits and invalid source readings."""
    hass.states.async_set(SOURCE_ENTITY_ID, "50")
    hass.states.async_set(OTHER_ENTITY_ID, "50")
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={
            **mock_config_entry.options,
            CONF_STATE_TYPE: StateTypes.NUMERIC_STATE,
            **limits,
        },
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(SOURCE_ENTITY_ID, value)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == expected


async def test_multiple_matches(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test source transitions update the complete list of matching entities."""
    await setup_integration(hass, mock_config_entry)
    hass.states.async_set(SOURCE_ENTITY_ID, "on")
    hass.states.async_set(OTHER_ENTITY_ID, "on")
    await hass.async_block_till_done()
    assert set(hass.states.get(ENTITY_ID).attributes[ATTR_ENTITIES]) == {
        SOURCE_ENTITY_ID,
        OTHER_ENTITY_ID,
    }
    hass.states.async_set(SOURCE_ENTITY_ID, "off")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).attributes[ATTR_ENTITIES] == [OTHER_ENTITY_ID]


async def test_source_state_removed(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test source state removal clears its matching status."""
    await setup_integration(hass, mock_config_entry)
    hass.states.async_set(SOURCE_ENTITY_ID, "on")
    await hass.async_block_till_done()
    hass.states.async_remove(SOURCE_ENTITY_ID)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "off"


async def test_label_membership(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    test_label: lr.LabelEntry,
) -> None:
    """Test sources added to a label are tracked and removed members no longer match."""
    await setup_integration(hass, mock_config_entry)
    added = entity_registry.async_get_or_create(
        "sensor", "test", "added", suggested_object_id="added"
    )
    entity_registry.async_update_entity(added.entity_id, labels={test_label.label_id})
    await hass.async_block_till_done()
    hass.states.async_set(added.entity_id, "on")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).attributes[ATTR_ENTITIES] == [added.entity_id]
    entity_registry.async_update_entity(added.entity_id, labels=set())
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "off"
    hass.states.async_set(added.entity_id, "off")
    hass.states.async_set(added.entity_id, "on")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "off"


async def test_label_registry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    label_registry: lr.LabelRegistry,
    test_label: lr.LabelEntry,
) -> None:
    """Test a label rename updates the name and deletion makes the helper unavailable."""
    await setup_integration(hass, mock_config_entry)
    unrelated = label_registry.async_create("Unrelated")
    label_registry.async_update(unrelated.label_id, name="Other label")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).attributes[ATTR_LABEL_NAME] == "test"
    label_registry.async_update(test_label.label_id, name="Renamed label")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).attributes[ATTR_LABEL_NAME] == "Renamed label"
    label_registry.async_delete(test_label.label_id)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "unavailable"


async def test_self_label(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    test_label: lr.LabelEntry,
) -> None:
    """Test assigning the watched label to the helper does not make it track itself."""
    await setup_integration(hass, mock_config_entry)
    entity_registry.async_update_entity(ENTITY_ID, labels={test_label.label_id})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "off"
    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).attributes[ATTR_ENTITIES] == []


async def test_entity_names(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
) -> None:
    """Test source names include the device and prefer user overrides."""
    source_entry = MockConfigEntry(domain="test")
    source_entry.add_to_hass(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=source_entry.entry_id,
        identifiers={("test", "source")},
        name="Device",
    )
    device_registry.async_update_device(device.id, name_by_user="My device")
    entity_registry.async_update_entity(
        SOURCE_ENTITY_ID, device_id=device.id, name="My source"
    )
    hass.states.async_set(SOURCE_ENTITY_ID, "on")
    await setup_integration(hass, mock_config_entry)
    assert hass.states.get(ENTITY_ID).attributes[ATTR_ENTITY_NAMES] == [
        "My device (My source)"
    ]


async def test_yaml_platform(hass: HomeAssistant, test_label: lr.LabelEntry) -> None:
    """Test legacy YAML platform setup constructs a correctly configured helper."""
    add_entities = Mock()
    await async_setup_platform(
        hass,
        {
            CONF_NAME: "Legacy",
            CONF_LABEL: test_label.label_id,
            CONF_STATE_TYPE: StateTypes.STATE,
            CONF_STATE_TO: "on",
        },
        add_entities,
    )
    sensor = add_entities.call_args.args[0][0]
    assert isinstance(sensor, LabelStateBinarySensor)
    assert sensor.name == "Legacy"
    assert sensor.unique_id is None
    assert sensor.is_on is False


async def test_missing_name_fallback(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test the name helper falls back to an entity ID when its registry entry is absent."""
    sensor = LabelStateBinarySensor(
        hass, "test", "Test", StateTypes.STATE, "on", None, None, None, "test"
    )
    sensor.hass = hass
    assert sensor._get_device_or_entity_name("sensor.missing") == "sensor.missing"  # noqa: SLF001
