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
      return 1;
    }

    render() {
      return ct.LitHtml `
        <ha-card>
          <div id="searchContainer">
          <div class="search-toolbar">
            <search-input>
              <ha-textfield id="searchText" icon="mdi:magnify" placeholder="${this.search_text}">
              <slot name="prefix" slot="leadingIcon">
		            <ha-icon icon="mdi:magnify" id="searchIcon" slot="prefix"></ha-icon>
              </slot>
              </ha-textfield>
            </search-input>
            </div>
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

      history.pushState(null, "", location);
      const event = new Event("location-changed", {
        bubbles: true,
        composed: true,
      });
      event.detail = { replace: false };
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
        #searchText {
          width: 100%;
        }
      `;
    }
  }

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