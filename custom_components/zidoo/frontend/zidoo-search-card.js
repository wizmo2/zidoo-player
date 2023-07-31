customElements.whenDefined('card-tools').then(() => {
  var ct = customElements.get('card-tools');

  class ZidooSearchCard extends ct.LitElement {

    static get properties() {
      return {
        config: {},
        hass: {},
      };
    }

    setConfig(config) {
      this.config = config;
      this.entity_id = this.config.entity;
      if (!this.entity_id)
        throw new Error("Add a valid Entity id in the Card Configuration!");

      this.buttons = this.config.buttons || ["video","movie","tvshow","music","album","artist"]

      this.search_text = this.config.search_text || "Media search...";
    }

    getCardSize() {
      return 4;
    }

    render() {
      return ct.LitHtml `
        <ha-card>
          <div id="searchContainer">
            <paper-input id="searchText"
                         no-label-float type="text" autocomplete="off"
                         label="${this.search_text}">
              <ha-icon icon="mdi:magnify" id="searchIcon"
                         slot="prefix"></ha-icon>
              <ha-icon-button slot="suffix"
                                 @click="${this._clearInput}"
                                 alt="Clear"
                                 title="Clear"><ha-icon icon="mdi:close"></ha-icon></ha-icon-button>
            </paper-input>
            <div class="sub-section">
              <div class="sub-heading">Search Media</div>
              ${(this.buttons.includes("video")) ? ct.LitHtml `
              <mwc-button id=${"video"} @click=${this._searchMedia}>
                <ha-icon id=${"video"} icon="hass:video" class="padded-right"></ha-icon>
                Videos
              </mwc-button>` : ''}
              ${(this.buttons.includes("movie")) ? ct.LitHtml `
              <mwc-button id=${"movie"} @click=${this._searchMedia}>
                <ha-icon id=${"movie"} icon="hass:movie" class="padded-right"></ha-icon>
                Movies
              </mwc-button>` : ''}
              ${(this.buttons.includes("tvshow")) ? ct.LitHtml `
              <mwc-button id=${"tvshow"} @click=${this._searchMedia}>
                <ha-icon id=${"tvshow"} icon="hass:television-classic" class="padded-right"></ha-icon>
                Tv Shows
              </mwc-button>` : ''}
              ${(this.buttons.includes("music")) ? ct.LitHtml `
              <mwc-button id=${"music"} @click=${this._searchMedia}>
                <ha-icon id=${"music"} icon="hass:music" class="padded-right"></ha-icon>
                Tracks
              </mwc-button>` : ''}
              ${(this.buttons.includes("album")) ? ct.LitHtml `
              <mwc-button id=${"album"} @click=${this._searchMedia}>
                <ha-icon id=${"album"} icon="hass:album" class="padded-right"></ha-icon>
                Albums
              </mwc-button>` : ''}
              ${(this.buttons.includes("artist")) ? ct.LitHtml `
              <mwc-button id=${"artist"} @click=${this._searchMedia}>
                <ha-icon id=${"artist"} icon="hass:account-music" class="padded-right"></ha-icon>
                Artists
              </mwc-button>` : ''}
            </div>
          </div>
        </ha-card>
      `;
    }

    _clearInput()
    {
      this.shadowRoot.getElementById('searchText').value = '';
      super.update()
    }

    _searchMedia(ev) {
      var searchType = ev.target.id
      var searchText = this.shadowRoot.getElementById('searchText').value;

      var location = `/media-browser/${this.entity_id}/${searchType}%2C${searchText?searchText+"*":searchType}`;

      history.replaceState(null, "", location);
      const event = new Event("location-changed", {
        bubbles: true,
        composed: true,
      });
      event.detail = { replace: true };
      this.dispatchEvent(event);
    }

    static get styles() {
      return ct.LitCSS `
        #searchContainer {
          width: 90%;
          display: block;
          margin-left: auto;
          margin-right: auto;
        }
          #searchIcon {
          padding: 10px;
        }
      `;
    }

    /*
    static getConfigElement() {
      return document.createElement("zidoo-search-editor");
    }
    */
  }

  /*
  class ZidoSearchEditor extends ct.LitElement {
    setConfig(config) {
      this._config = config;
      this._included_domains = ["media_player"]

      this.results = [];
      this._getEntities();
    }

    _getEntities() {
      this.results = [];

      try {
        for (var entity_id in this.hass.states) {
          if ( this._included_domains.includes(entity_id.split(".")[0])) {
            this.results.push(entity_id);
          }
        }
      } catch (err) {
        console.warn(err);
      }
    }

    configChanged(newConfig) {
      const event = new Event("config-changed", {
        bubbles: true,
        composed: true,
      });
      event.detail = { config: newConfig };
      this.dispatchEvent(event);
    }

    render() {
      var rows = this.results.map((entity_id) => this._createResultRow(entity_id));
      return ct.LitHtml `

        <div id="searchContainer">
          <ha-select id="searchText"
                       label="Select the Zidoo Entity">
            ${(rows.length > 0) ?
              ct.LitHtml `<div id="results">${rows}</div>`
            : ''}
          </ha-select>
        </div>
    `;
    }

    _createResultRow(entity_id) {
      var row = ct.createEntityRow({entity: entity_id});
      row.addEventListener("click", () => ct.moreInfo(entity_id));
      row.hass = this.hass;
      return row;
    }

    static get styles() {
      return ct.LitCSS `
        #searchContainer {
          width: 90%;
          display: block;
          margin-left: auto;
          margin-right: auto;
        }
          #searchIcon {
          padding: 10px;
        }
      `;
    }

  }

  customElements.define("zidoo-search-editor", ZidoSearchEditor);
  */
  customElements.define('zidoo-search-card', ZidooSearchCard);

  });

  setTimeout(() => {
    if(customElements.get('card-tools')) return;
    customElements.define('zidoo-search-card', class extends HTMLElement{
      setConfig() { throw new Error("Can't find card-tools. See https://github.com/thomasloven/lovelace-card-tools");}
    });
  }, 2000);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "zidoo-search-card",
    name: "Zidoo Search Card",
    preview: true,
    description: "Card to launch media search"
  });