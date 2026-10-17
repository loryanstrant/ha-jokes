/**
 * ha-jokes-card — a custom Lovelace card for the ha_jokes integration.
 *
 * Displays the current joke, its source, an "Explain it" button (AI explanation
 * via the ha_jokes.explain_joke service), a "New joke" button (forces a refresh),
 * and a conditional explanation panel (rendered as Markdown via HA's own <ha-markdown>),
 * which can sit below or beside the joke. Ships a visual editor built on <ha-form>.
 *
 * Dependency-free vanilla web component — no build step. Bundled with the integration and
 * auto-registered as a frontend resource, so it needs no manual "add resource" step.
 *
 * Version is kept in lockstep with the integration's manifest.json.
 */

const CARD_VERSION = "1.7.0";

console.info(
  `%c HA-JOKES-CARD %c v${CARD_VERSION} `,
  "color: white; background: #3f51b5; font-weight: 700;",
  "color: #3f51b5; background: white; font-weight: 700;"
);

class HaJokesCard extends HTMLElement {
  static getStubConfig() {
    return { entity: "sensor.joke" };
  }

  static getConfigElement() {
    return document.createElement("ha-jokes-card-editor");
  }

  setConfig(config) {
    this._config = {
      entity: "sensor.joke",
      explanation_entity: "sensor.joke_explanation",
      title: "Joke of the Moment",
      show_buttons: true,
      show_source: true,
      // "below" stacks the explanation under the joke; "side" puts it alongside and
      // falls back to stacking on narrow cards (see the flex-wrap rule).
      explanation_position: "below",
      // Optional sizing, both in px. height is a *minimum* so the card does not jump
      // as the explanation appears and disappears; width caps how wide it grows.
      height: 0,
      width: 0,
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

    // This <style> lives in ha-card's light DOM, so it registers as a *document*
    // stylesheet — every selector must be scoped to `ha-jokes-card` or generic class
    // names like .title/.hidden leak out and restyle the rest of the HA frontend.
    const style = document.createElement("style");
    style.textContent = `
      ha-jokes-card .wrap { padding: 16px; }
      ha-jokes-card .title {
        font-size: 1.25rem; font-weight: 600; margin: 0 0 12px 0;
        color: var(--primary-text-color); display: flex; align-items: center; gap: 8px;
      }
      ha-jokes-card .joke {
        font-size: 1.05rem; line-height: 1.5; color: var(--primary-text-color);
        border-left: 4px solid var(--primary-color, #03a9f4);
        padding: 4px 0 4px 14px; margin: 0;
        /* Two-part jokes arrive with a newline between setup and punchline — keep it. */
        white-space: pre-line;
      }
      ha-jokes-card .empty { color: var(--secondary-text-color); font-style: italic; }
      /* Layout container. "below" stacks; "side" sits the explanation next to the joke
         but wraps back to stacked once the card is too narrow for two columns. */
      ha-jokes-card .body { display: flex; gap: 14px; }
      ha-jokes-card .body.below { flex-direction: column; }
      ha-jokes-card .body.side { flex-direction: row; flex-wrap: wrap; align-items: flex-start; }
      ha-jokes-card .body.side > .main,
      ha-jokes-card .body.side > .explanation { flex: 1 1 260px; min-width: 0; }
      /* .explanation owns its top margin when stacked; the flex gap handles it otherwise. */
      ha-jokes-card .body.side > .explanation { margin-top: 0; }
      ha-jokes-card .meta {
        margin-top: 10px; font-size: 0.8rem; color: var(--secondary-text-color);
        display: flex; gap: 12px; flex-wrap: wrap;
      }
      ha-jokes-card .buttons { display: flex; gap: 8px; margin-top: 14px; }
      ha-jokes-card .btn {
        flex: 1; cursor: pointer; border: none; border-radius: 12px;
        padding: 10px 8px; font-size: 0.9rem; font-weight: 500;
        display: flex; align-items: center; justify-content: center; gap: 6px;
        background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff);
      }
      ha-jokes-card .btn.secondary {
        background: var(--secondary-background-color, #e0e0e0);
        color: var(--primary-text-color);
      }
      ha-jokes-card .btn:active { opacity: 0.85; }
      ha-jokes-card .btn ha-icon { --mdc-icon-size: 20px; }
      ha-jokes-card .explanation {
        margin-top: 14px; padding: 12px 14px; border-radius: 12px;
        background: var(--secondary-background-color, rgba(0,0,0,0.05));
      }
      ha-jokes-card .explanation .eh {
        font-weight: 600; font-size: 0.9rem; margin-bottom: 6px;
        color: var(--primary-text-color); display: flex; align-items: center; gap: 6px;
      }
      ha-jokes-card .explanation .et {
        font-size: 0.95rem; line-height: 1.45; color: var(--primary-text-color);
      }
      /* Only the plain-text fallback keeps source newlines. Never put pre-line on
         <ha-markdown>: it inherits into the shadow DOM and turns the whitespace between
         marked's generated tags into visible blank lines. */
      ha-jokes-card .explanation .et-plain { white-space: pre-line; }
      ha-jokes-card .explanation ha-markdown { display: block; }
      ha-jokes-card .explanation ha-markdown > *:first-child { margin-top: 0; }
      ha-jokes-card .explanation ha-markdown > *:last-child { margin-bottom: 0; }
      ha-jokes-card .hidden { display: none; }
    `;

    const wrap = document.createElement("div");
    wrap.className = "wrap";
    wrap.innerHTML = `
      <div class="title"><ha-icon icon="mdi:emoticon-happy-outline"></ha-icon><span class="title-text"></span></div>
      <div class="body">
        <div class="main">
          <p class="joke"></p>
          <div class="meta">
            <span class="src hidden"></span>
            <span class="upd"></span>
          </div>
          <div class="buttons hidden">
            <button class="btn explain" type="button"><ha-icon icon="mdi:lightbulb-question-outline"></ha-icon>Explain it</button>
            <button class="btn secondary newjoke" type="button"><ha-icon icon="mdi:dice-multiple-outline"></ha-icon>New joke</button>
          </div>
        </div>
        <div class="explanation hidden">
          <div class="eh"><ha-icon icon="mdi:lightbulb-on-outline"></ha-icon>Explanation</div>
          <div class="et et-plain"></div>
        </div>
      </div>
    `;

    card.appendChild(style);
    card.appendChild(wrap);
    this.innerHTML = "";
    this.appendChild(card);

    // Cache references.
    this._els = {
      card,
      body: wrap.querySelector(".body"),
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
      explanationMarkdown: null,
    };

    // The AI writes the explanation in markdown (**bold**, numbered lists, nested bullets).
    // Render it with HA's own <ha-markdown>, which sanitises and themes for us — it lives in
    // the core frontend bundle, so by the time this card is registered it is available.
    // Older cores without it fall back to the plain-text div, which at least keeps the
    // paragraph breaks via .et-plain.
    if (window.customElements.get("ha-markdown")) {
      const md = document.createElement("ha-markdown");
      md.setAttribute("breaks", "");
      md.className = "et";
      this._els.explanationText.replaceWith(md);
      this._els.explanationText = null;
      this._els.explanationMarkdown = md;
    }

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

    // Layout + optional sizing.
    const side = cfg.explanation_position === "side";
    els.body.classList.toggle("side", side);
    els.body.classList.toggle("below", !side);
    els.card.style.minHeight = cfg.height > 0 ? `${cfg.height}px` : "";
    els.card.style.maxWidth = cfg.width > 0 ? `${cfg.width}px` : "";

    const rawJoke = st && st.attributes ? st.attributes.joke : "";
    // Normalise CRLF and collapse blank lines so a setup/punchline pair sits on two
    // consecutive lines rather than being split by a big gap (see .joke pre-line).
    const joke = rawJoke
      ? String(rawJoke).replace(/\r\n?/g, "\n").replace(/\n{2,}/g, "\n").trim()
      : "";
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

    // Explanation panel — shown when the explanation entity reports "Explained" AND the
    // explanation still belongs to the joke on screen. The integration clears it when the
    // joke rotates, but this guard also covers the brief window before that state lands,
    // and older integration versions that never reported joke_id at all.
    const exp = this._hass.states[cfg.explanation_entity];
    const explained = exp && exp.state === "Explained";
    const explainedFor = exp && exp.attributes ? exp.attributes.joke_id : undefined;
    const currentJokeId = st && st.attributes ? st.attributes.joke_id : undefined;
    // Only compare when both sides actually reported an id — providers such as Geek Jokes
    // and Yo Mama send none, and an absent id must not hide a valid explanation.
    const stale = !!explainedFor && !!currentJokeId && explainedFor !== currentJokeId;
    if (explained && !stale && exp.attributes && exp.attributes.explanation) {
      const text = exp.attributes.explanation;
      if (els.explanationMarkdown) {
        els.explanationMarkdown.content = text;
      } else {
        els.explanationText.textContent = text;
      }
      els.explanation.classList.remove("hidden");
    } else {
      els.explanation.classList.add("hidden");
    }
  }
}

const EDITOR_SCHEMA = [
  { name: "entity", selector: { entity: { domain: "sensor" } } },
  { name: "explanation_entity", selector: { entity: { domain: "sensor" } } },
  { name: "title", selector: { text: {} } },
  {
    name: "explanation_position",
    selector: {
      select: {
        mode: "dropdown",
        options: [
          { value: "below", label: "Below the joke" },
          { value: "side", label: "Beside the joke" },
        ],
      },
    },
  },
  {
    name: "height",
    selector: {
      number: { min: 0, max: 1200, step: 10, mode: "box", unit_of_measurement: "px" },
    },
  },
  {
    name: "width",
    selector: {
      number: { min: 0, max: 2000, step: 10, mode: "box", unit_of_measurement: "px" },
    },
  },
  { name: "show_source", selector: { boolean: {} } },
  { name: "show_buttons", selector: { boolean: {} } },
];

// ha-form renders the raw key name when it cannot find a label, so these are required.
const EDITOR_LABELS = {
  entity: "Joke entity",
  explanation_entity: "Explanation entity",
  title: "Card heading",
  explanation_position: "Explanation position",
  height: "Minimum height (0 = automatic)",
  width: "Maximum width (0 = full width)",
  show_source: "Show the joke source and age",
  show_buttons: "Show the Explain it / New joke buttons",
};

class HaJokesCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    // ha-form needs hass to resolve its selectors, so wait for it.
    if (!this._hass || !this._config) return;

    if (!this._form) {
      const form = document.createElement("ha-form");
      form.computeLabel = (schema) => EDITOR_LABELS[schema.name] || schema.name;
      form.addEventListener("value-changed", (ev) => {
        // Stop the inner event so only our config-changed reaches the editor host.
        ev.stopPropagation();
        this.dispatchEvent(
          new CustomEvent("config-changed", {
            // ha-form hands back the whole object, untouched keys (including `type`)
            // included, so it can be forwarded as the new config as-is.
            detail: { config: ev.detail.value },
            bubbles: true,
            composed: true,
          })
        );
      });
      this.appendChild(form);
      this._form = form;
    }

    this._form.hass = this._hass;
    this._form.schema = EDITOR_SCHEMA;
    this._form.data = this._config;
  }
}

function registerCard() {
  // Always read window.customElements fresh — see waitForHaRegistry below.
  if (!window.customElements.get("ha-jokes-card")) {
    window.customElements.define("ha-jokes-card", HaJokesCard);
  }
  // Must be registered in the same registry as the card, for the same reason.
  if (!window.customElements.get("ha-jokes-card-editor")) {
    window.customElements.define("ha-jokes-card-editor", HaJokesCardEditor);
  }
  // Only advertise the card once the element really is defined. Publishing this entry
  // while the element is missing is what makes the picker spin forever.
  window.customCards = window.customCards || [];
  if (!window.customCards.some((card) => card.type === "ha-jokes-card")) {
    window.customCards.push({
      type: "ha-jokes-card",
      name: "Jokes Card",
      description: "Shows the current joke with Explain and New joke actions.",
      // Must be true: HA's card picker maps this to `showElement`, and with false it renders
      // a bare description placeholder instead of a live preview of the card.
      preview: true,
      documentationURL: "https://github.com/loryanstrant/ha-jokes",
    });
  }
}

// Home Assistant replaces window.customElements with a scoped-registry polyfill while its
// core bundle boots. The integration injects this file via add_extra_js_url as a bare
// import(), which races that boot: if we win, `define` lands in the *native* registry, HA
// then swaps in its own, and the definition is lost. window.customCards survives (it is a
// plain window property), so the picker lists the card, awaits whenDefined() on a registry
// that will never have it, and renders a spinner forever.
//
// So: wait until HA's own elements are visible in the CURRENT registry before registering.
// window.customElements must be re-read every tick — it is a different object before and
// after the swap — which is also why we must not call customElements.whenDefined() at module
// top level: that would bind to the native registry's method and might never fire.
const HA_REGISTRY_TIMEOUT_MS = 10000;
const registrationStartedAt = Date.now();

(function waitForHaRegistry() {
  if (
    window.customElements.get("home-assistant") ||
    Date.now() - registrationStartedAt > HA_REGISTRY_TIMEOUT_MS
  ) {
    registerCard();
    return;
  }
  setTimeout(waitForHaRegistry, 50);
})();
