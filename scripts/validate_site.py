#!/usr/bin/env python3
"""Validate the static BeanLedger marketing site before publishing."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
CNAME_PATH = ROOT / "CNAME"

REQUIRED_ASSETS = [
    "assets/app-icon.png",
    "assets/screenshots/iphone-home.png",
    "assets/screenshots/iphone-capture.png",
    "assets/screenshots/iphone-widgets.png",
    "assets/screenshots/watch-home.png",
]

REQUIRED_LINKS = {
    "https://apps.apple.com/app/id6739036460",
    "https://my.feishu.cn/wiki/ZThAw9DpIiP1c5kpA5ecevW7n0g",
    "https://my.feishu.cn/wiki/LMQ7wdGL5iYMySkqAjFcPa7xnjf",
    "https://my.feishu.cn/wiki/CAsdwDoQCi7GNXk94locljnnnwd",
}

FORBIDDEN_LINKS = {
    "https://my.feishu.cn/wiki/OmKCwVtreii2j3kZFrCc0lzcnbb",
    "https://my.feishu.cn/wiki/BYUQwg2KRidwW7ka2dJcWms6n2e",
    "https://my.feishu.cn/wiki/RCTPwbGY6iIpdmkP4AUcWpFYn0b",
    "https://my.feishu.cn/wiki/INLGw3WtQiNyO1kOPWXcG2WEnQc",
}

SUPPORTED_LOCALES = {
    "en-US",
    "zh-Hans",
    "zh-Hant",
    "de-DE",
    "es-ES",
    "fr-FR",
    "it",
    "ja",
    "ko",
    "ms",
    "nl-NL",
    "pl",
    "pt-BR",
    "ru",
    "th",
    "tr",
    "vi",
}

FORBIDDEN_MARKERS = [
    "iCloud.com.maples7",
    "com.maples7.BeanLedger",
    "TradeManager",
    "SwiftData schema",
    "CloudKit container",
]


class MarketingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()
        self.images: set[str] = set()
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a" and attrs_dict.get("href"):
            self.links.add(attrs_dict["href"])
        elif tag == "img" and attrs_dict.get("src"):
            self.images.add(attrs_dict["src"])
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def fail(message: str) -> None:
    print(f"site validation failed: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not INDEX_PATH.exists():
        fail("index.html is missing")
    if CNAME_PATH.read_text(encoding="utf-8").strip() != "beanledger.maples7.com":
        fail("CNAME must be beanledger.maples7.com")

    html = INDEX_PATH.read_text(encoding="utf-8")
    parser = MarketingHTMLParser()
    parser.feed(html)

    if "BeanLedger" not in parser.title:
        fail("HTML title must include BeanLedger")
    for asset in REQUIRED_ASSETS:
        if not (ROOT / asset).exists():
            fail(f"required asset is missing: {asset}")
        if asset not in parser.images:
            fail(f"index.html does not reference required asset: {asset}")
    missing_links = sorted(REQUIRED_LINKS - parser.links)
    if missing_links:
        fail("required links are missing: " + ", ".join(missing_links))
    leaked_links = sorted(FORBIDDEN_LINKS & parser.links)
    if leaked_links:
        fail("obsolete documentation links are still present: " + ", ".join(leaked_links))
    missing_locales = sorted(locale for locale in SUPPORTED_LOCALES if f"'{locale}'" not in html and f'"{locale}"' not in html)
    if missing_locales:
        fail("supported locales are missing: " + ", ".join(missing_locales))
    for marker in FORBIDDEN_MARKERS:
        if marker in html:
            fail(f"page leaks internal-only marker: {marker}")
    if re.search(r"\bTrades?\b", html):
        fail("user-facing page copy must say Transaction, not Trade")
    if re.search(r"fonts\.googleapis|googletagmanager|google-analytics|plausible\.io|umami\.is|<script[^>]+https?", html, re.I):
        fail("page must not load third-party fonts or analytics")

    print("site validation passed")


if __name__ == "__main__":
    main()