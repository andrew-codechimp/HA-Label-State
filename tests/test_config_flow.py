"""Tests for Label State menu, configuration, validation, and options flows."""

from unittest.mock import AsyncMock

import pytest
from custom_components.label_state.const import (
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_NOT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    DOMAIN,
    StateTypes,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .const import DEFAULT_NAME


@pytest.mark.parametrize(
    ("state_type", "settings"),
    [
        pytest.param(StateTypes.STATE, {CONF_STATE_TO: "on"}, id="state"),
        pytest.param(StateTypes.NOT_STATE, {CONF_STATE_NOT: "off"}, id="not-state"),
        pytest.param(
            StateTypes.NUMERIC_STATE,
            {CONF_STATE_LOWER_LIMIT: 0},
            id="numeric-lower-zero",
        ),
        pytest.param(
            StateTypes.NUMERIC_STATE, {CONF_STATE_UPPER_LIMIT: 90}, id="numeric-upper"
        ),
        pytest.param(
            StateTypes.NUMERIC_STATE,
            {CONF_STATE_LOWER_LIMIT: 10, CONF_STATE_UPPER_LIMIT: 90},
            id="numeric-range",
        ),
    ],
)
async def test_user_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    state_type: StateTypes,
    settings: dict[str, str | float],
) -> None:
    """Test each menu choice creates a helper with the correct state type and options."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.MENU
    assert set(result["menu_options"]) == {
        StateTypes.STATE,
        StateTypes.NOT_STATE,
        StateTypes.NUMERIC_STATE,
    }
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": state_type}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == state_type
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_NAME: DEFAULT_NAME, CONF_LABEL: "test", **settings}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME
    assert result["version"] == 1
    assert result["data"] == {}
    assert result["options"] == {
        CONF_NAME: DEFAULT_NAME,
        CONF_LABEL: "test",
        CONF_STATE_TYPE: state_type,
        **settings,
    }
    mock_setup_entry.assert_awaited_once()


@pytest.mark.usefixtures("mock_setup_entry")
async def test_numeric_validation(hass: HomeAssistant) -> None:
    """Test a numeric helper requires at least one limit and permits correcting the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": StateTypes.NUMERIC_STATE}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_NAME: DEFAULT_NAME, CONF_LABEL: "test"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "upper_or_lower_not_specified"}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: DEFAULT_NAME, CONF_LABEL: "test", CONF_STATE_UPPER_LIMIT: 90},
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.parametrize(
    ("state_type", "settings", "changed"),
    [
        pytest.param(
            StateTypes.STATE,
            {CONF_STATE_TO: "on"},
            {CONF_STATE_TO: "Custom state"},
            id="state",
        ),
        pytest.param(
            StateTypes.NOT_STATE,
            {CONF_STATE_NOT: "off"},
            {CONF_STATE_NOT: "Custom state"},
            id="not-state",
        ),
        pytest.param(
            StateTypes.NUMERIC_STATE,
            {CONF_STATE_LOWER_LIMIT: 10},
            {CONF_STATE_LOWER_LIMIT: 20},
            id="numeric",
        ),
    ],
)
async def test_options(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    state_type: StateTypes,
    settings: dict[str, str | float],
    changed: dict[str, str | float],
) -> None:
    """Test options select the saved state type, suggest values, and preserve the name."""
    mock_config_entry.add_to_hass(hass)
    original = {**mock_config_entry.options, CONF_STATE_TYPE: state_type, **settings}
    hass.config_entries.async_update_entry(mock_config_entry, options=original)
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == state_type
    assert {
        key.schema: key.description["suggested_value"]
        for key in result["data_schema"].schema
        if "suggested_value" in (key.description or {})
    } == {CONF_LABEL: "test", **settings}
    updated = {CONF_LABEL: "other", **changed}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], updated
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {**original, **updated}
    assert mock_config_entry.title == DEFAULT_NAME
    assert mock_config_entry.data == {}
