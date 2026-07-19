/**
 * ha-jokes-card — a custom Lovelace card for the ha_jokes integration.
 *
 * Displays the current joke, its source, an "Explain it" button (AI explanation
 * via the ha_jokes.explain_joke service), a "New joke" button (forces a refresh),
 * and a conditional explanation panel. Dependency-free vanilla web component — no
 * build step. Bundled with the integration and auto-registered as a frontend
 * resource, so it needs no manual "add resource" step.
 *
 * Version is kept in lockstep with the integration's manifest.json.
 */

const CARD_VERSION = "1.4.0";

console.info(
  `%c HA-JOKES-CARD %c v${CARD_VERSION} `,
  "color: white; background: #3f51b5; font-weight: 700;",
  "color: #3f51b5; background: white; font-weight: 700;"
);

class HaJokesCard extends HTMLElement {
  static getStubConfig() {
    return { entity: "sensor.joke" };
  }

  setConfig(config) {
    this._config = {
      entity: "sensor.joke",
      explanation_entity: "sensor.joke_explanation",
      title: "Joke of the Moment",
      show_buttons: true,
      show_source: true,
      ...(config || {}),
    };
    // Rebuild the DOM on (re)config.
    this._built = false;
    if (this._hass) this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 3;
  }

  _relativeTime(iso) {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    if (isNaN(then)) return "";
    const secs = Math.max(0, Math.round((Date.now() - then) / 1000));
    if (secs < 60) return `${secs}s ago`;
    const mins = Math.round(secs / 60);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.round(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.round(hrs / 24)}d ago`;
  }

  _build() {
    const card = document.createElement("ha-card");

    const style = document.createElement("style");
    style.textContent = `
      .wrap { padding: 16px; }
      .title {
        font-size: 1.25rem; font-weight: 600; margin: 0 0 12px 0;
        color: var(--primary-text-color); display: flex; align-items: center; gap: 8px;
      }
      .joke {
        font-size: 1.05rem; line-height: 1.5; color: var(--primary-text-color);
        border-left: 4px solid var(--primary-color, #03a9f4);
        padding: 4px 0 4px 14px; margin: 0;
      }
      .empty { color: var(--secondary-text-color); font-style: italic; }
      .meta {
        margin-top: 10px; font-size: 0.8rem; color: var(--secondary-text-color);
        display: flex; gap: 12px; flex-wrap: wrap;
      }
      .buttons { display: flex; gap: 8px; margin-top: 14px; }
      .btn {
        flex: 1; cursor: pointer; border: none; border-radius: 12px;
        padding: 10px 8px; font-size: 0.9rem; font-weight: 500;
        display: flex; align-items: center; justify-content: center; gap: 6px;
        background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff);
      }
      .btn.secondary {
        background: var(--secondary-background-color, #e0e0e0);
        color: var(--primary-text-color);
      }
      .btn:active { opacity: 0.85; }
      .btn ha-icon { --mdc-icon-size: 20px; }
      .explanation {
        margin-top: 14px; padding: 12px 14px; border-radius: 12px;
        background: var(--secondary-background-color, rgba(0,0,0,0.05));
      }
      .explanation .eh {
        font-weight: 600; font-size: 0.9rem; margin-bottom: 6px;
        color: var(--primary-text-color); display: flex; align-items: center; gap: 6px;
      }
      .explanation .et {
        font-size: 0.95rem; line-height: 1.45; color: var(--primary-text-color);
      }
      .hidden { display: none; }
    `;

    const wrap = document.createElement("div");
    wrap.className = "wrap";
    wrap.innerHTML = `
      <div class="title"><ha-icon icon="mdi:emoticon-happy-outline"></ha-icon><span class="title-text"></span></div>
      <p class="joke"></p>
      <div class="meta">
        <span class="src hidden"></span>
        <span class="upd"></span>
      </div>
      <div class="buttons hidden">
        <button class="btn explain" type="button"><ha-icon icon="mdi:lightbulb-question-outline"></ha-icon>Explain it</button>
        <button class="btn secondary newjoke" type="button"><ha-icon icon="mdi:dice-multiple-outline"></ha-icon>New joke</button>
      </div>
      <div class="explanation hidden">
        <div class="eh"><ha-icon icon="mdi:lightbulb-on-outline"></ha-icon>Explanation</div>
        <div class="et"></div>
      </div>
    `;

    card.appendChild(style);
    card.appendChild(wrap);
    this.innerHTML = "";
    this.appendChild(card);

    // Cache references.
    this._els = {
      titleText: wrap.querySelector(".title-text"),
      joke: wrap.querySelector(".joke"),
      meta: wrap.querySelector(".meta"),
      src: wrap.querySelector(".src"),
      upd: wrap.querySelector(".upd"),
      buttons: wrap.querySelector(".buttons"),
      explainBtn: wrap.querySelector(".explain"),
      newBtn: wrap.querySelector(".newjoke"),
      explanation: wrap.querySelector(".explanation"),
      explanationText: wrap.querySelector(".et"),
    };

    // Wire buttons once.
    this._els.explainBtn.addEventListener("click", () => {
      if (this._hass) this._hass.callService("ha_jokes", "explain_joke");
    });
    this._els.newBtn.addEventListener("click", () => {
      if (this._hass) {
        this._hass.callService("homeassistant", "update_entity", {
          entity_id: this._config.entity,
        });
      }
    });

    this._built = true;
  }

  _render() {
    if (!this._config || !this._hass) return;
    if (!this._built) this._build();

    const els = this._els;
    const cfg = this._config;
    const st = this._hass.states[cfg.entity];

    els.titleText.textContent = cfg.title;

    const joke = st && st.attributes ? st.attributes.joke : "";
    if (joke) {
      els.joke.textContent = joke;
      els.joke.classList.remove("empty");
    } else {
      els.joke.textContent = "No joke right now — the next one is on its way…";
      els.joke.classList.add("empty");
    }

    // Source + updated meta.
    const source = st && st.attributes ? st.attributes.source : "";
    if (cfg.show_source && source) {
      els.src.textContent = `🎲 ${source}`;
      els.src.classList.remove("hidden");
    } else {
      els.src.classList.add("hidden");
    }
    const upd = st && st.attributes ? st.attributes.last_updated : "";
    const rel = this._relativeTime(upd);
    els.upd.textContent = rel ? `🕒 ${rel}` : "";

    // Buttons.
    els.buttons.classList.toggle("hidden", !cfg.show_buttons);

    // Explanation panel — shown when the explanation entity reports "Explained".
    const exp = this._hass.states[cfg.explanation_entity];
    const explained = exp && exp.state === "Explained";
    if (explained && exp.attributes && exp.attributes.explanation) {
      els.explanationText.textContent = exp.attributes.explanation;
      els.explanation.classList.remove("hidden");
    } else {
      els.explanation.classList.add("hidden");
    }
  }
}

customElements.define("ha-jokes-card", HaJokesCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "ha-jokes-card",
  name: "Jokes Card",
  description: "Shows the current joke with Explain and New joke actions.",
  preview: false,
  documentationURL: "https://github.com/loryanstrant/ha-jokes",
});
