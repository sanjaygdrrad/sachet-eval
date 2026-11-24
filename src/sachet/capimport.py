"""Import a CAP 1.2 alert (Common Alerting Protocol, the international standard for public
warnings) as a Sachet case.

The first ``<info>`` block in the source language becomes the official ``source``
(headline + description + instruction). Every other language block, and any short
summaries found in ``<parameter>`` elements (e.g. ``gati:summary160``), become
``candidates`` to evaluate. ``must_keep`` is left for a person to fill in, because
choosing which names are safety-critical is a judgement call.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"c": "urn:oasis:names:tc:emergency:cap:1.2"}
SUMMARY_PARAMS = ("gati:summary160",)


def _t(el: ET.Element, tag: str) -> str:
    return (el.findtext(f"c:{tag}", default="", namespaces=NS) or "").strip()


def _info_text(info: ET.Element) -> str:
    return "\n\n".join(p for p in (_t(info, "headline"), _t(info, "description"), _t(info, "instruction")) if p)


def _toml_str(s: str) -> str:
    s = s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{s}\n"""'


def _toml_line(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cap_to_case_toml(path: str | Path, source_lang: str = "ne", case_id: str | None = None) -> str:
    root = ET.parse(path).getroot()
    infos = root.findall("c:info", NS)
    if not infos:
        raise ValueError(f"{path}: no <info> blocks found (is this a CAP 1.2 file?)")
    lang = lambda i: _t(i, "language").lower()
    src = next((i for i in infos if lang(i).startswith(source_lang)), infos[0])

    web = _t(src, "web")
    for p in src.findall("c:parameter", NS):
        if _t(p, "valueName") == "gati:sourceUrl":
            web = _t(p, "value") or web
    cid = case_id or re.sub(r"[^a-z0-9-]+", "-", Path(path).stem.lower()).strip("-")

    out = [
        f"# Imported from CAP 1.2: {Path(path).name}",
        f"# Sender: {_t(root, 'sender')}. Note from the CAP file: {_t(root, 'note')[:300]}",
        "# TODO: fill in must_keep (the place, river and station names that must survive).",
        f"id = {_toml_line(cid)}",
        f"language = {_toml_line(lang(src).split('-')[0] or source_lang)}",
        f"issuer = {_toml_line(_t(src, 'senderName'))}",
        f"issued = {_toml_line(_t(root, 'sent'))}",
        f"source_url = {_toml_line(web)}",
        f"relayed_by = {_toml_line('Gati' if 'Gati' in _t(root, 'note') else '')}",
        f"note = {_toml_line('Imported from a CAP 1.2 alert. Candidates are the other-language versions and summaries contained in the same alert.')}",
        "",
        f"source = {_toml_str(_info_text(src))}",
        "",
        "must_keep = []",
        "may_drop = []",
        "may_add = []",
    ]
    for info in infos:
        if info is not src:
            out += ["", "[[candidates]]", f"system = {_toml_line('cap-' + lang(info) + ' (in the same alert)')}", f"text = {_toml_str(_info_text(info))}"]
    for info in infos:
        for p in info.findall("c:parameter", NS):
            name = _t(p, "valueName")
            if name in SUMMARY_PARAMS and _t(p, "value"):
                out += ["", "[[candidates]]", f"system = {_toml_line(name + ' ' + lang(info))}", 'channel = "sms"', f"text = {_toml_str(_t(p, 'value'))}"]
    return "\n".join(out) + "\n"
