"""Test label_state config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.label_state.const import (
    CONF_LABEL,
    CONF_STATE_LOWER_LIMIT,
    CONF_STATE_TO,
    CONF_STATE_TYPE,
    CONF_STATE_UPPER_LIMIT,
    DOMAIN,
)

from .const import DEFAULT_NAME


async def test_form_sensor(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test we get the form for sensor."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("step_id") == "user"
    assert result.get("type") is FlowResultType.MENU

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: DEFAULT_NAME,
            CONF_STATE_TYPE: "state",
            CONF_LABEL: "test_label",
            CONF_STATE_TO: "on",
        },
    )
    await hass.async_block_till_done()

    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result.get("version") == 1
    assert result.get("options") == {
        CONF_NAME: DEFAULT_NAME,
        CONF_STATE_TYPE: "state",
        CONF_LABEL: "test_label",
        CONF_STATE_TO: "on",
    }

    assert len(mock_setup_entry.mock_calls) == 1
