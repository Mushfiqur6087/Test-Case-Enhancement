"""DOM tree parsing and interactive element extraction."""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from test_case_enhancement.browser.dom_builder import DomTreeBuilder


@dataclass
class DOMTextNode:
    """DOMTextNode class."""
    text: str
    is_visible: bool
    parent: Optional["DOMElementNode"] = None


@dataclass
class DOMElementNode:
    """DOMElementNode class."""
    tag_name: str
    xpath: str
    attributes: Dict[str, str]
    children: List[Any]
    is_visible: bool
    is_interactive: bool
    inner_text: str = ""
    parent: Optional["DOMElementNode"] = None


class DOMTreeParser:
    """Wrap a Playwright page to build a DOM tree and extract selector map."""

    def __init__(self, page) -> None:
        """Initialize the __init__ method."""
        if page is None:
            raise ValueError("No page object provided for parsing.")
        self.page = page
        self.dom_tree: Optional[DOMElementNode] = None
        self._raw_json: Optional[Dict[str, Any]] = None
        self._counts: Dict[str, int] = {}

    def parse(self) -> DOMElementNode:
        """
        Crawl the page via DomTreeBuilder, store raw JSON, and
        build the in-memory tree of DOMElementNode/DOMTextNode.
        """
        data = DomTreeBuilder(self.page, debug_mode=False).get_dom_tree()
        self._raw_json = data["tree"]
        self._counts.clear()
        self.dom_tree = self._build_element(self._raw_json, parent_xpath="/html[1]/", parent=None)
        return self.dom_tree

    def _build_element(
        self,
        node: Dict[str, Any],
        parent_xpath: str,
        parent: Optional[DOMElementNode],
    ) -> DOMElementNode:
        """Recursively construct DOMElementNode (and its text-node children)."""
        tag = node["nodeName"]

        if "xpath" in node and node["xpath"]:
            xpath = node["xpath"]
        else:
            key = f"{parent_xpath}{tag}"
            self._counts[key] = self._counts.get(key, 0) + 1
            xpath = f"{parent_xpath}{tag}[{self._counts[key]}]"

        is_visible = node.get("isVisible", True)
        is_interactive = node.get("isInteractive", False)
        inner_text = node.get("innerText", "")

        elm = DOMElementNode(
            tag_name=tag,
            xpath=xpath,
            attributes=node.get("attributes", {}),
            children=[],
            is_visible=is_visible,
            is_interactive=is_interactive,
            inner_text=inner_text,
            parent=parent,
        )

        for child in node.get("children", []):
            if isinstance(child, dict) and child.get("nodeName") == "#text":
                text = child.get("textContent", "").strip()
                if text:
                    elm.children.append(DOMTextNode(text=text, is_visible=is_visible, parent=elm))
            elif isinstance(child, dict):
                elm.children.append(self._build_element(child, xpath + "/", elm))

        return elm

    def get_dom_string(self) -> str:
        """Return an indented string representation of the DOM tree."""
        if not self.dom_tree:
            raise ValueError("DOM tree not built, call parse() first.")
        lines: List[str] = []
        self._dump(self.dom_tree, indent="", lines=lines)
        return "\n".join(lines)

    def _dump(self, node: Any, indent: str, lines: List[str]) -> None:
        """Helper to serialize tree into a list of lines."""
        if isinstance(node, DOMTextNode):
            lines.append(f"{indent}\u2514\u2500\u2500 DOMTextNode(text={node.text!r}, is_visible={node.is_visible})")
        else:
            attrs_str = ""
            if node.attributes:
                attrs_list = [f"{k}='{v}'" for k, v in node.attributes.items()]
                attrs_str = f", attributes={{{', '.join(attrs_list)}}}"

            inner_text_str = ""
            if node.inner_text:
                inner_text_str = f", inner_text={node.inner_text!r}"

            lines.append(
                f"{indent}DOMElementNode(tag={node.tag_name!r}, xpath={node.xpath!r}, "
                f"is_visible={node.is_visible}, is_interactive={node.is_interactive}{attrs_str}{inner_text_str})"
            )
            for i, child in enumerate(node.children):
                last = i == len(node.children) - 1
                self._dump(child, indent + ("    " if last else "\u2502   "), lines)

    def selector_map(self) -> Dict[int, DOMElementNode]:
        """
        Flatten and return only the interactive elements in encounter order:
        {0: <button node>, 1: <input node>, ...}
        """
        if not self.dom_tree:
            raise ValueError("DOM tree not built, call parse() first.")
        self._flat_index = 0
        self._flat_map: Dict[int, DOMElementNode] = {}
        self._flatten(self.dom_tree)
        return self._flat_map

    def _flatten(self, node: DOMElementNode) -> None:
        """Recursively collect interactive AND visible nodes into _flat_map."""
        if node.is_interactive and node.is_visible:
            self._flat_map[self._flat_index] = node
            self._flat_index += 1
        for child in node.children:
            if isinstance(child, DOMElementNode):
                self._flatten(child)

    def selector_map_json(self) -> str:
        """Return a JSON map of interactive elements with full details."""
        sel_map = self.selector_map()
        out: Dict[int, Dict[str, Any]] = {}
        for idx, node in sel_map.items():
            out[idx] = {
                "tag_name": node.tag_name,
                "xpath": node.xpath,
                "attributes": node.attributes,
                "is_visible": node.is_visible,
                "is_interactive": node.is_interactive,
                "inner_text": node.inner_text,
                "children": [
                    {
                        "text": child.text,
                        "is_visible": child.is_visible,
                        "parent": child.parent.xpath if child.parent else None
                    }
                    for child in node.children
                    if isinstance(child, DOMTextNode)
                ],
                "parent": node.parent.xpath if node.parent else None
            }
        return json.dumps(out, indent=2)

    def get_selector_map_string(self) -> str:
        """Return a human-readable list of all interactive elements."""
        if not self.dom_tree:
            raise ValueError("DOM tree not built, call parse() first.")

        self._flat_index = 0
        self._flat_map: Dict[int, str] = {}
        _skip_attrs = {"class", "style"}

        def traverse(node: DOMElementNode, depth: int) -> None:
            """traverse method/function."""
            if node.is_interactive:
                index = self._flat_index
                self._flat_index += 1
                indent = "    " * depth
                attrs = " ".join(
                    f"{k}='{v}'"
                    for k, v in node.attributes.items()
                    if k not in _skip_attrs and v != ""
                )
                attrs_str = f" {attrs}" if attrs else ""
                # Truncate inner_text to avoid bloating the prompt with
                # full-page text from container elements like <body>/<div>
                inner_text = node.inner_text
                if inner_text:
                    inner_text = " ".join(inner_text.split())  # collapse whitespace/newlines
                    if len(inner_text) > 100:
                        inner_text = inner_text[:100] + "..."
                inner_text_str = f" inner_text='{inner_text}'" if inner_text else ""
                tag_str = f"<{node.tag_name}{attrs_str}{inner_text_str} />"
                self._flat_map[index] = f"{indent}[{index}]{tag_str}"
            for child in node.children:
                if isinstance(child, DOMElementNode):
                    traverse(child, depth + 1)

        traverse(self.dom_tree, depth=0)
        lines = [line.lstrip(" ") for line in self._flat_map.values()]
        return "\n".join(lines)
