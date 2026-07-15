import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


class _HtmlContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.label_targets: list[str] = []
        self.inputs: dict[str, dict[str, str | None]] = {}
        self.meta: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if element_id := values.get("id"):
            self.ids.append(element_id)
        if tag == "label" and values.get("for"):
            self.label_targets.append(str(values["for"]))
        if tag == "input" and values.get("id"):
            self.inputs[str(values["id"])] = values
        if tag == "meta":
            self.meta.append(values)


def test_browser_manifest_is_valid_and_references_existing_python_files() -> None:
    manifest = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    files = manifest["files"]

    source_entries = [
        source.removeprefix("{FROM}/")
        for source in files
        if source.startswith("{FROM}/")
    ]
    assert "fabrication.py" in source_entries
    assert len(source_entries) == len(set(source_entries))
    for relative_path in source_entries:
        assert (ROOT / "src" / "realkey" / relative_path).is_file(), relative_path


def test_all_python_sources_parse() -> None:
    for source in (ROOT / "src" / "realkey").glob("*.py"):
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    for source in (ROOT / "main.py", ROOT / "worker.py"):
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))


def test_literal_resource_references_exist() -> None:
    pattern = re.compile(r'["\'](resources/[^"\']+\.(?:svg|step|stl|png))["\']')
    missing: list[str] = []
    for source in (ROOT / "src" / "realkey").glob("*.py"):
        for relative_path in pattern.findall(source.read_text(encoding="utf-8")):
            if not (ROOT / relative_path).is_file():
                missing.append(f"{source.name}: {relative_path}")
    assert not missing


def test_browser_dependencies_are_version_pinned() -> None:
    worker = (ROOT / "worker.py").read_text(encoding="utf-8")
    assert 'build123d==0.11.0' in worker
    assert 'typing-extensions==4.15.0' in worker


def test_html_accessibility_and_private_share_defaults() -> None:
    parser = _HtmlContractParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    assert len(parser.ids) == len(set(parser.ids))
    assert set(parser.label_targets) <= set(parser.ids)
    assert "checked" not in parser.inputs["share-settings"]
    assert "checked" not in parser.inputs["share-generate"]
    assert any(
        meta.get("name") == "referrer" and meta.get("content") == "no-referrer"
        for meta in parser.meta
    )


def test_literal_web_bindings_reference_existing_html_ids() -> None:
    parser = _HtmlContractParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    binding_pattern = re.compile(r'web\.page\["([^"]+)"\]')
    bound_ids: set[str] = set()
    for source in (ROOT / "src" / "realkey").glob("*.py"):
        bound_ids.update(binding_pattern.findall(source.read_text(encoding="utf-8")))
    bound_ids.update(binding_pattern.findall((ROOT / "main.py").read_text(encoding="utf-8")))

    assert bound_ids <= set(parser.ids)


def test_browser_generation_contract_is_transactional() -> None:
    foreground = (ROOT / "src" / "realkey" / "web_main.py").read_text(encoding="utf-8")
    worker = (ROOT / "worker.py").read_text(encoding="utf-8")

    assert "await model_view.loadObject" in foreground
    assert 'f"{base_url}#' in foreground
    assert "uuid.uuid4()" in worker
    assert "Mesher()" in worker
    assert '"temp.stl"' not in worker
