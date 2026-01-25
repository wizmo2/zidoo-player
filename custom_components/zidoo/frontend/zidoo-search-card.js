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
        throw new Error("Add a valid media player 'entity' in the Card Configuration!");

      this.buttons = this.config.buttons || ["video","movie","tvshow","music","album","artist"]

      this.search_text = this.config.search_text || "Media search...";
    }

    getCardSize() {
      return 1;
    }

    static getStubConfig() {
        return {'entity': 'media_player.' };
    }

    static get styles() {
      return ct.LitCSS `
        ha-card {
          overflow: hidden;
        }
        #searchContainer {
          display: block;
          margin-left: auto;
          margin-right: auto;
        }
        #searchContainer search-input {
          display: block;
        }
        #searchIcon {
          padding: 10px;
        }
        #searchText {
          width: 100%;
        }
        #searchButtons {
          padding: 5px 7px;
        }
        #searchButtons ha-progress-button {
          margin: 3px;
        }
      `;
    }

    render() {
      return ct.LitHtml `
        <ha-card>
          <div id="searchContainer">
          <div class="search-toolbar">
            <search-input .hass=${this.hass}>
              <ha-textfield id="searchText" icon="mdi:magnify" placeholder="${this.search_text}">
              <slot name="prefix" slot="leadingIcon">
		            <ha-icon icon="mdi:magnify" id="searchIcon" slot="prefix"></ha-icon>
              </slot>
              </ha-textfield>
            </search-input>
            </div>
            <div id="searchButtons" class="sub-section">
              <div class="sub-heading">Search Media</div>
              ${(this.buttons.includes("video")) ? ct.LitHtml `
              <ha-progress-button id=${"video"} @click=${this._searchMedia}>
                <ha-icon id=${"video"} icon="hass:video" class="padded-right"></ha-icon>
                Videos
              </ha-progress-button>` : ''}
              ${(this.buttons.includes("movie")) ? ct.LitHtml `
              <ha-progress-button id=${"movie"} @click=${this._searchMedia}>
                <ha-icon id=${"movie"} icon="hass:movie" class="padded-right"></ha-icon>
                Movies
              </ha-progress-button>` : ''}
              ${(this.buttons.includes("tvshow")) ? ct.LitHtml `
              <ha-progress-button id=${"tvshow"} @click=${this._searchMedia}>
                <ha-icon id=${"tvshow"} icon="hass:television-classic" class="padded-right"></ha-icon>
                Tv Shows
              </ha-progress-button>` : ''}
              ${(this.buttons.includes("music")) ? ct.LitHtml `
              <ha-progress-button id=${"music"} @click=${this._searchMedia}>
                <ha-icon id=${"music"} icon="hass:music" class="padded-right"></ha-icon>
                Tracks
              </ha-progress-button>` : ''}
              ${(this.buttons.includes("album")) ? ct.LitHtml `
              <ha-progress-button id=${"album"} @click=${this._searchMedia}>
                <ha-icon id=${"album"} icon="hass:album" class="padded-right"></ha-icon>
                Albums
              </ha-progress-button>` : ''}
              ${(this.buttons.includes("artist")) ? ct.LitHtml `
              <ha-progress-button id=${"artist"} @click=${this._searchMedia}>
                <ha-icon id=${"artist"} icon="hass:account-music" class="padded-right"></ha-icon>
                Artists
              </ha-progress-button>` : ''}
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
    description: "Zidoo Search Card to launch media browser with search query"
  });