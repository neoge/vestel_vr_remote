"""Config flow for Vestel VR Remote integration."""

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class VestelVrRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	"""Handle a config flow for Vestel VR Remote."""

	VERSION = 1

	async def async_step_user(self, user_input=None) -> FlowResult:
		"""Handle the initial step."""
		errors = {}

		if user_input is not None:
			host = user_input[CONF_HOST]
			name = user_input[CONF_NAME]
			try:
				await self._async_test_connection(host)
			except Exception:
				errors["base"] = "cannot_connect"
			else:
				await self.async_set_unique_id(host)
				self._abort_if_unique_id_configured()
				return self.async_create_entry(title=name, data={CONF_HOST: host, CONF_NAME: name})

		return self.async_show_form(
			step_id="user",
			data_schema=vol.Schema({
				vol.Required(CONF_HOST): str,
				vol.Required(CONF_NAME, default="Vestel TV"): str,
			}),
			errors=errors,
		)

	async def _async_test_connection(self, host: str) -> None:
		"""Test connectivity to the TV by sending a harmless request (Info key)."""
		url = f"http://{host}:56789/apps/vr/remote"
		xml = '<?xml version="1.0" ?><remote><key code="1018"/></remote>'  # Info key for testing
		headers = {"Content-Type": "text/plain; charset=ISO-8859-1"}

		session = async_get_clientsession(self.hass)
		async with session.post(url, data=xml, headers=headers, timeout=5) as response:
			if response.status != 200:
				raise Exception("Connection failed")
