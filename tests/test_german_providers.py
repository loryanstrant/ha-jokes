"""Tests for the opt-in German joke providers (WitzAPI and Deine-Mutter-API).

The providers are exercised through the real aiohttp client against a local
aiohttp test server, so status handling, JSON decoding and UTF-8 behave exactly
as they would against the live APIs.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import partial

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_jokes.config_flow import JokesConfigFlow, JokesOptionsFlow
from custom_components.ha_jokes.const import (
    ATTR_JOKE,
    ATTR_JOKE_ID,
    ATTR_SOURCE,
    CONF_PROVIDERS,
    DEFAULT_PROVIDERS,
    DOMAIN,
    PROVIDER_DEINEMUTTER,
    PROVIDER_WITZAPI,
)
from custom_components.ha_jokes.sensor import JokesDataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.update_coordinator import UpdateFailed

WITZ_JOKE = (
    "Was macht ein Drache im Fußballstadion? Die Leute anfeuern. Ärger? Öde! Übel!"
)
MUTTER_JOKE = "Deine Mutter ist so hässlich, vor der hat sogar Chuck Norris Angst."


Responder = Callable[[], web.Response]


def _json(body: str, status: int = 200) -> Responder:
    return partial(
        web.Response,
        body=body.encode("utf-8"),
        status=status,
        content_type="application/json",
        charset="utf-8",
    )


@pytest.fixture
async def joke_server(socket_enabled):
    """Serve canned responses on localhost; tests fill in `responses[path]`.

    A float instead of a responder makes the server stall that many seconds.
    """
    responses: dict[str, Responder | float] = {}

    async def handler(request: web.Request) -> web.Response:
        responder = responses[request.path]
        if isinstance(responder, float):
            await asyncio.sleep(responder)
            responder = _json("{}")
        return responder()

    app = web.Application()
    app.router.add_get("/{tail:.*}", handler)
    server = TestServer(app)
    await server.start_server()
    server.responses = responses
    yield server
    await server.close()


def _coordinator(
    hass: HomeAssistant, server: TestServer, providers: list[str]
) -> JokesDataUpdateCoordinator:
    """Build a coordinator whose provider URLs point at the local test server."""
    coordinator = JokesDataUpdateCoordinator(hass, 5, providers)
    for provider in coordinator._providers:
        provider["url"] = str(server.make_url(f"/{provider['name']}"))
    return coordinator


async def _fetch(
    coordinator: JokesDataUpdateCoordinator,
    name: str,
    timeout: aiohttp.ClientTimeout | None = None,
):
    provider = next(p for p in coordinator._providers if p["name"] == name)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        return await coordinator._fetch_from_provider(session, provider)


def test_german_providers_are_opt_in() -> None:
    """Existing installs keep their providers: the German ones are off by default."""
    assert PROVIDER_WITZAPI not in DEFAULT_PROVIDERS
    assert PROVIDER_DEINEMUTTER not in DEFAULT_PROVIDERS


async def test_default_coordinator_does_not_query_german_providers(
    hass: HomeAssistant,
) -> None:
    coordinator = JokesDataUpdateCoordinator(hass, 5, [])
    names = {p["name"] for p in coordinator._providers}
    assert names == set(DEFAULT_PROVIDERS)


async def test_witzapi_url_requests_one_german_joke(hass: HomeAssistant) -> None:
    coordinator = JokesDataUpdateCoordinator(hass, 5, [PROVIDER_WITZAPI])
    assert coordinator._providers[0]["url"] == (
        "https://witzapi.de/api/joke/?limit=1&language=de"
    )


async def test_witzapi_success_preserves_umlauts(
    hass: HomeAssistant, joke_server: TestServer
) -> None:
    joke_server.responses["/witzapi"] = _json(
        f'[{{"text": "{WITZ_JOKE}", "language": "de"}}]'
    )
    coordinator = _coordinator(hass, joke_server, [PROVIDER_WITZAPI])

    result = await _fetch(coordinator, PROVIDER_WITZAPI)

    assert result == {
        ATTR_JOKE: WITZ_JOKE,
        ATTR_JOKE_ID: "",
        ATTR_SOURCE: "witzapi.de",
    }


async def test_deinemutter_success_decodes_unicode_escapes(
    hass: HomeAssistant, joke_server: TestServer
) -> None:
    # The live API escapes non-ASCII characters (h\u00e4sslich).
    escaped = MUTTER_JOKE.replace("ä", "\\u00e4")
    assert "\\u00e4" in escaped
    joke_server.responses["/deine_mutter"] = _json(f'{{"joke": "{escaped}"}}')
    coordinator = _coordinator(hass, joke_server, [PROVIDER_DEINEMUTTER])

    result = await _fetch(coordinator, PROVIDER_DEINEMUTTER)

    assert result == {
        ATTR_JOKE: MUTTER_JOKE,
        ATTR_JOKE_ID: "",
        ATTR_SOURCE: "deine-mutter.timkley.dev",
    }


@pytest.mark.parametrize(
    ("provider", "response"),
    [
        (PROVIDER_WITZAPI, _json("[]")),
        (PROVIDER_WITZAPI, _json('[{"language": "de"}]')),
        (PROVIDER_WITZAPI, _json('[{"text": ""}]')),
        (PROVIDER_WITZAPI, _json('{"text": "kein Array"}')),
        (PROVIDER_WITZAPI, _json('["nur ein String"]')),
        (PROVIDER_WITZAPI, _json("[{not json")),
        (PROVIDER_WITZAPI, _json('{"error": "boom"}', status=500)),
        (
            PROVIDER_WITZAPI,
            partial(web.Response, text="<html>Too Many Requests</html>", status=429),
        ),
        (PROVIDER_DEINEMUTTER, _json("{}")),
        (PROVIDER_DEINEMUTTER, _json('{"joke": ""}')),
        (PROVIDER_DEINEMUTTER, _json('["Deine Mutter"]')),
        (PROVIDER_DEINEMUTTER, _json("{not json")),
        (PROVIDER_DEINEMUTTER, _json('{"joke": "x"}', status=503)),
        (
            PROVIDER_DEINEMUTTER,
            partial(web.Response, text="Deine Mutter", content_type="text/html"),
        ),
    ],
    ids=[
        "witzapi-empty-array",
        "witzapi-missing-text",
        "witzapi-empty-text",
        "witzapi-object-not-array",
        "witzapi-non-object-item",
        "witzapi-malformed-json",
        "witzapi-http-500",
        "witzapi-http-429-html",
        "deinemutter-missing-joke",
        "deinemutter-empty-joke",
        "deinemutter-array-not-object",
        "deinemutter-malformed-json",
        "deinemutter-http-503",
        "deinemutter-html-content-type",
    ],
)
async def test_bad_responses_are_skipped(
    hass: HomeAssistant,
    joke_server: TestServer,
    provider: str,
    response: Responder,
) -> None:
    joke_server.responses[f"/{provider}"] = response
    coordinator = _coordinator(hass, joke_server, [provider])

    assert await _fetch(coordinator, provider) is None


@pytest.mark.parametrize("provider", [PROVIDER_WITZAPI, PROVIDER_DEINEMUTTER])
async def test_timeout_is_skipped(
    hass: HomeAssistant, joke_server: TestServer, provider: str
) -> None:
    joke_server.responses[f"/{provider}"] = 1.0
    coordinator = _coordinator(hass, joke_server, [provider])

    result = await _fetch(coordinator, provider, aiohttp.ClientTimeout(total=0.1))

    assert result is None


async def test_failing_german_provider_falls_back_to_the_other(
    hass: HomeAssistant, joke_server: TestServer
) -> None:
    joke_server.responses["/witzapi"] = _json("[]")
    joke_server.responses["/deine_mutter"] = _json(f'{{"joke": "{MUTTER_JOKE}"}}')
    coordinator = _coordinator(
        hass, joke_server, [PROVIDER_WITZAPI, PROVIDER_DEINEMUTTER]
    )

    # Provider order is shuffled per update, so repeat to cover both orders.
    for _ in range(5):
        data = await coordinator._async_update_data()
        assert data[ATTR_JOKE] == MUTTER_JOKE
        assert data[ATTR_SOURCE] == "deine-mutter.timkley.dev"


async def test_all_german_providers_failing_raises_update_failed(
    hass: HomeAssistant, joke_server: TestServer
) -> None:
    joke_server.responses["/witzapi"] = _json("[]")
    joke_server.responses["/deine_mutter"] = _json("{}", status=500)
    coordinator = _coordinator(
        hass, joke_server, [PROVIDER_WITZAPI, PROVIDER_DEINEMUTTER]
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_config_and_options_flow_offer_german_providers_unticked(
    hass: HomeAssistant,
) -> None:
    config_flow = JokesConfigFlow()
    config_flow.hass = hass
    _assert_offered_but_unticked(await config_flow.async_step_user())

    entry = MockConfigEntry(
        domain=DOMAIN, options={CONF_PROVIDERS: list(DEFAULT_PROVIDERS)}
    )
    entry.add_to_hass(hass)
    options_flow = JokesOptionsFlow(entry)
    options_flow.hass = hass
    _assert_offered_but_unticked(await options_flow.async_step_init())


def _assert_offered_but_unticked(result: dict) -> None:
    assert result["type"] is FlowResultType.FORM
    schema = result["data_schema"].schema
    field = next(key for key in schema if key == CONF_PROVIDERS)
    assert {PROVIDER_WITZAPI, PROVIDER_DEINEMUTTER} <= set(schema[field].options)
    assert PROVIDER_WITZAPI not in field.default()
    assert PROVIDER_DEINEMUTTER not in field.default()
