"""Button platform for Vestel VR Remote."""

import aiohttp

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, KEYS


async def async_setup_entry(
	hass: HomeAssistant,
	entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up the button platform."""
	host = entry.data[CONF_HOST]
	name = entry.data[CONF_NAME]
	entities = [VestelVrRemoteButton(host, name, key["code"], key["function"], key.get("icon")) for key in KEYS]
	async_add_entities(entities)


class VestelVrRemoteButton(ButtonEntity):
	"""Representation of a Vestel VR Remote button."""

	def __init__(self, host: str, name: str, code: str, function: str, icon: str = None) -> None:
		"""Initialize the button."""
		self._host = host
		self._name = name
		self._code = code
		self._attr_name = f"{name} {function}"
		self._attr_unique_id = f"{host}_{code}"
		if icon:
			self._attr_icon = icon

	@property
	def device_info(self) -> DeviceInfo:
		"""Return device info for the registry."""
		return DeviceInfo(
			identifiers={(DOMAIN, self._host)},
			name=self._name,
			manufacturer="Vestel",
			model="Virtual Remote",
		)

	async def async_press(self) -> None:
		"""Handle the button press."""
		url = f"http://{self._host}:56789/apps/vr/remote"
		xml = f'<?xml version="1.0" ?><remote><key code="{self._code}"/></remote>'
		headers = {"Content-Type": "text/plain; charset=ISO-8859-1"}

		async with aiohttp.ClientSession() as session:
			await session.post(url, data=xml, headers=headers)
