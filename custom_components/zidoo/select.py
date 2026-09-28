"""Support for Zidoo Media Player select entities."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZidooCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zidoo select entities from a config entry."""
    coordinator: ZidooCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            ZidooAudioSelect(coordinator, config_entry),
            ZidooSubtitleSelect(coordinator, config_entry),
            ZidooZoomSelect(coordinator, config_entry),
        ]
    )


class ZidooAudioSelect(CoordinatorEntity[ZidooCoordinator], SelectEntity):
    """Zidoo Audio Track Select Entity."""

    def __init__(self, coordinator: ZidooCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_audio_track"
        self._attr_name = f"{config_entry.title} Audio Track"
        self._attr_icon = "mdi:speaker-wireless"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Zidoo",
            name=config_entry.title,
        )

    @property
    def available(self) -> bool:
        return len(self.coordinator.audio_tracks) > 0

    @property
    def options(self) -> list[str]:
        return [track.get("title") for track in self.coordinator.audio_tracks if track.get("title")]

    @property
    def current_option(self) -> str | None:
        current_idx = self.coordinator.player._current_audio
        for track in self.coordinator.audio_tracks:
            if track.get("index") == current_idx:
                return track.get("title")
        return None

    async def async_select_option(self, option: str) -> None:
        for track in self.coordinator.audio_tracks:
            if track.get("title") == option:
                await self.coordinator.player.set_audio(track.get("index"))
                await self.coordinator.async_request_refresh()
                break


class ZidooSubtitleSelect(CoordinatorEntity[ZidooCoordinator], SelectEntity):
    """Zidoo Subtitle Track Select Entity."""

    def __init__(self, coordinator: ZidooCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_subtitle_track"
        self._attr_name = f"{config_entry.title} Subtitles"
        self._attr_icon = "mdi:subtitles"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Zidoo",
            name=config_entry.title,
        )

    @property
    def available(self) -> bool:
        return len(self.coordinator.subtitle_tracks) > 0

    @property
    def options(self) -> list[str]:
        return [track.get("title") for track in self.coordinator.subtitle_tracks if track.get("title")]

    @property
    def current_option(self) -> str | None:
        current_idx = self.coordinator.player._current_subtitle
        for track in self.coordinator.subtitle_tracks:
            if track.get("index") == current_idx:
                return track.get("title")
        return None

    async def async_select_option(self, option: str) -> None:
        for track in self.coordinator.subtitle_tracks:
            if track.get("title") == option:
                await self.coordinator.player.set_subtitle(track.get("index"))
                await self.coordinator.async_request_refresh()
                break

class ZidooZoomSelect(CoordinatorEntity[ZidooCoordinator], SelectEntity):
    """Zidoo Zoom Mode Select Entity."""

    def __init__(self, coordinator: ZidooCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_zoom_mode"
        self._attr_name = f"{config_entry.title} Zoom Mode"
        self._attr_icon = "mdi:aspect-ratio"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Zidoo",
            name=config_entry.title,
        )

    @property
    def available(self) -> bool:
        return len(self.coordinator.zoom_modes) > 0

    @property
    def options(self) -> list[str]:
        return list(self.coordinator.zoom_modes.values())

    @property
    def current_option(self) -> str | None:
        current_idx = self.coordinator.player._current_zoom
        return self.coordinator.zoom_modes.get(current_idx)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.player.set_zoom(option)
        await self.coordinator.async_request_refresh()