"""Fixtures for Label State tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from custom_components.label_state.const import (
    CONF_LABEL,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    DOMAIN,
    StateTypes,
)
from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, label_registry as lr

from .const import DEFAULT_NAME


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Use the Home Assistant snapshot serializer."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in Home Assistant."""


@pytest.fixture(autouse=True)
def freeze_setup_time(freezer: FrozenDateTimeFactory) -> None:
    """Keep entity timestamps and scheduled callbacks stable."""
    freezer.move_to("2026-07-01T12:00:00+00:00")


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Mock integration setup when testing flows in isolation."""
    with patch(
        "custom_components.label_state.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_config_entry(request: pytest.FixtureRequest) -> MockConfigEntry:
    """Create a helper entry with default options and optional overrides."""
    return MockConfigEntry(
        domain=DOMAIN,
        version=1,
        minor_version=1,
        entry_id="helper-entry",
        title=DEFAULT_NAME,
        data={},
        options={
            CONF_NAME: DEFAULT_NAME,
            CONF_LABEL: "test",
            CONF_STATE_TYPE: StateTypes.STATE,
            CONF_STATE_TO: "on",
            **getattr(request, "param", {}),
        },
    )


@pytest.fixture
def test_label(label_registry: lr.LabelRegistry) -> lr.LabelEntry:
    """Create the label monitored by the helper."""
    return label_registry.async_create("test")


@pytest.fixture
def labeled_sources(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, test_label: lr.LabelEntry
) -> None:
    """Register two labeled sources and publish initial states."""
    for suffix in ("source", "other"):
        entity = entity_registry.async_get_or_create(
            "sensor",
            "test",
            suffix,
            suggested_object_id=f"test_{suffix}",
            original_name=suffix.capitalize(),
        )
        entity_registry.async_update_entity(
            entity.entity_id, labels={test_label.label_id}
        )
        hass.states.async_set(entity.entity_id, "off")
