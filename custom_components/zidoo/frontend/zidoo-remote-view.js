class ZidooDashboardStrategy {
  static async generate(config, hass) {
    // Query all data we need. We will make it available to views by storing it in strategy options.
    const [devices, entities] = await Promise.all([
      hass.callWS({ type: "config/device_registry/list" }),
      hass.callWS({ type: "config/entity_registry/list" }),
    ]);

    const view_list = [];

    entities.forEach(entity => {
      if (entity.platform == "zidoo" && entity.entity_id.startsWith('media_player.')) {
        const remote = Object.values(entities).find(entity2 =>
          entity2.entity_id.startsWith('remote.') && entity2.device_id == entity.device_id
        )
        view_list.push({
          strategy: {
            type: "custom:zidoo-remote",
            entity: entity.entity_id,
            remote: remote.entity_id,
          },
          title: (entity.name == null) ? entity.original_name : entity.original_name,
        })
      }
    });
    return { views: view_list };
  }
}

class ZidooRemoteStrategy {
  static async generate(config, hass) {
    const cards = [
      {
        type: "button", name: "PopMenu", show_name: false, icon: "mdi:menu-close", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Info" } }
      },
      {
        type: "button", name: "Up", show_name: false, icon: "mdi:arrow-up-bold", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Up" } }
      },
      {
        type: "button", name: "Home", show_name: false, icon: "mdi:home-outline", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Home" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.PopUp" } }
      },
      {
        type: "button", name: "Audio", show_name: false, icon: "mdi:television-speaker", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.set_audio", target: { entity_id: `${config.remote}` } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Audio" } }
      },
      {
        type: "button", name: "Left", show_name: false, icon: "mdi:arrow-left-bold", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Left" } },
      },
      {
        type: "button", name: "OK", show_name: false, icon: "mdi:check-bold", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Ok" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Select" } }
      },
      {
        type: "button", name: "Right", show_name: false, icon: "mdi:arrow-right-bold", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Right" } }
      },
      {
        type: "button", name: "Subtitle", show_name: false, icon: "mdi:subtitles-outline", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.set_subtitle", target: { entity_id: `${config.remote}` }, }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Subtitle" } }
      },
      {
        type: "button", name: "Back", show_name: false, icon: "mdi:backspace-outline", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Back" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Cancel" } }
      },
      {
        type: "button", name: "Down", show_name: false, icon: "mdi:arrow-down-bold", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Down" } }
      },
      {
        type: "button", name: "Menu", show_name: false, icon: "mdi:menu", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Menu" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Resolution" } }
      },
      {
        type: "button", name: "App", show_name: false, icon: "mdi:exit-to-app", show_icon: true, entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.Pip" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.APP.Switch" } }
      },
      {
        type: "button", name: "Prev", show_name: false, icon: "mdi:skip-backward", show_icon: true, type: "button", entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.MediaPrev" } }
      },
      {
        type: "button", name: "Backwards", show_name: false, icon: "mdi:rewind", show_icon: true, type: "button", entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.MediaBackwards" } }, hold_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.PopUp" } }
      },
      {
        type: "button", name: "Forwards", show_name: false, icon: "mdi:fast-forward", show_icon: true, type: "button", entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.MediaForwards" } }
      },
      {
        type: "button", name: "Next", show_name: false, icon: "mdi:skip-forward", show_icon: true, type: "button", entity: `${config.entity}`, tap_action: { action: "call-service", service: "remote.send_command", target: { entity_id: `${config.remote}` }, data: { command: "Key.MediaNext" } }
      },
    ];
    return {
      cards: [
        { type: "media-control", entity: `${config.entity}` },
        { type: "grid", columns: 4, cards, },
        { type: "custom:zidoo-search-card", entity: `${config.entity}` }
      ],
    };
  }
}

customElements.define("ll-strategy-zidoo-dashboard", ZidooDashboardStrategy);
customElements.define("ll-strategy-zidoo-remote", ZidooRemoteStrategy);