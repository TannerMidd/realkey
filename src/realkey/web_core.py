import math
from typing import Iterable

from pyscript import web, when


class Element:
    def __init__(self, web_element: web.ElementCollection) -> None:
        self._web_element = web_element

    @property
    def enabled(self) -> bool:
        return not self._web_element.disabled

    @enabled.setter
    def enabled(self, value: bool):
        if value:
            self._web_element.removeAttribute("disabled")  # type: ignore
        else:
            self._web_element.disabled = True

    @property
    def html(self) -> str:
        return str(self._web_element.innerHTML)

    @html.setter
    def html(self, value: str):
        """Set authored, trusted markup. Use ``text`` for runtime values."""
        self._web_element.innerHTML = value

    @property
    def text(self) -> str:
        return str(self._web_element.textContent)

    @text.setter
    def text(self, value: str):
        self._web_element.textContent = value

    def hide_popover(self):
        if hasattr(self._web_element, "hidePopover"):
            self._web_element.hidePopover()  # type: ignore

    def _set_class_bool(self, class_name: str, value: bool):
        if value:
            if class_name not in self._web_element.classes:
                self._web_element.classes.add(class_name)
        else:
            self._web_element.classes.discard(class_name)  # type: ignore

    @property
    def hidden(self) -> bool:
        return "hide" in self._web_element.classes

    @hidden.setter
    def hidden(self, value: bool):
        self._set_class_bool("hide", value)

    @property
    def active(self) -> bool:
        return "active" in self._web_element.classes

    @active.setter
    def active(self, value: bool):
        self._set_class_bool("active", value)


class StringValueElement(Element):
    def __init__(self, web_element: web.ElementCollection) -> None:
        super().__init__(web_element)

    @property
    def value(self) -> str:
        return str(self._web_element.value)

    @property
    def stripped_value(self) -> str:
        return str(self._web_element.value).strip()

    @value.setter
    def value(self, v: str):
        self._web_element.value = v


class FloatValueElement(Element):
    def __init__(self, web_element: web.ElementCollection) -> None:
        super().__init__(web_element)

    @property
    def value(self) -> float:
        return float(str(self._web_element.value))

    @property
    def stripped_value(self) -> float:
        return float(str(self._web_element.value).strip())

    @value.setter
    def value(self, v: float):
        self._web_element.value = v


class OptionElement(StringValueElement):
    def __init__(self, web_element: web.ElementCollection) -> None:
        super().__init__(web_element)

    @property
    def selected(self) -> bool:
        if hasattr(self._web_element, "selected"):
            return bool(self._web_element.selected)
        return False

    @selected.setter
    def selected(self, value: bool):
        if value:
            self._web_element.selected = True
        else:
            self._web_element.removeAttribute("selected")  # type: ignore

    def __str__(self):
        return f"{self._web_element.value} : {self._web_element.innerHTML} : {self.selected}"


class OptionElementList(list[OptionElement]):
    def __init__(self, iterable: Iterable[OptionElement]) -> None:
        super().__init__(iterable)

    @property
    def selected(self):
        for option in self:
            if option.selected:
                return option
        return self[0]

    def __str__(self):
        strs = [str(e) for e in self]
        return f"[{",".join(strs)}]"


class SelectElement(Element):
    def __init__(self, web_element: web.ElementCollection) -> None:
        super().__init__(web_element)

    def populate(self, null_string: str, options_dict: dict[str, dict[str, str]]):
        self._web_element.replaceChildren()  # type: ignore
        if len(null_string) > 0:
            self._web_element.options.add(value="null", html=null_string)  # type: ignore
        for optgroup, options in options_dict.items():
            if len(optgroup) > 0:
                group = web.optgroup(label=optgroup)
                self._web_element.append(group)  # type: ignore
                for value, html in options.items():
                    opt = web.option(innerHTML=html, value=value)
                    group.append(opt)  # type: ignore
            else:
                for value, html in options.items():
                    self._web_element.options.add(value=value, html=html)  # type: ignore

    @property
    def options(self) -> OptionElementList:
        options = OptionElementList([])

        for child in self._web_element.children:
            if "optgroup" == child.get_tag_name():
                for child in child.children:
                    options.append(OptionElement(child))
            else:
                options.append(OptionElement(child))
        return options

    @property
    def selected_value(self) -> str:
        return self.options.selected.value

    @selected_value.setter
    def selected_value(self, tag: str):
        for option in self.options:
            if tag == option.value:
                option.selected = True
                return
        raise ValueError(f'No option with value "{tag}" in select')

    @property
    def selected_html(self) -> str:
        return self.options.selected.html


class LengthInputElement(FloatValueElement):
    def __init__(self, web_element: web.ElementCollection, label: str | None = None) -> None:
        super().__init__(web_element)

        self._set_class_bool("length-input", True)
        wrapper_id = str(self._web_element.getAttribute("id"))  # type: ignore
        accessible_label = label or wrapper_id.replace("-", " ").title()
        self._input = web.input_(
            id=f"{wrapper_id}-value",
            type="number",
            value="0.000",
            min="0.001",
            max="1000",
            step="0.001",
            required=True,
            classes=["length-input-text"],
        )
        self._input.setAttribute("aria-label", f"{accessible_label} value")  # type: ignore
        self._units = web.select(id=f"{wrapper_id}-units", classes=["length-input-select"])
        self._units.setAttribute("aria-label", f"{accessible_label} units")  # type: ignore
        self._mm = web.option(value="mm", innerHTML="mm")
        self._inch = web.option(value="in", innerHTML="in")
        self._resolution = 3

        self._units.append(self._mm)
        self._units.append(self._inch)

        self._web_element.append(self._input)  # type: ignore
        self._web_element.append(self._units)  # type: ignore

        when("change", self._units)(self.unit_change)
        when("input", self._input)(self.validate)
        when("invalid", self._input)(self.invalid_input)

    def unit_change(self):
        if self._units.options.selected == self._mm:
            self._resolution = 3
            self._input.step = "0.001"
            self.value = self.value * 25.4
        elif self._units.options.selected == self._inch:
            self._resolution = 5
            self._input.step = "0.00001"
            self.value = self.value / 25.4
        self.validate()

    def validate(self):
        try:
            value = self.value
            valid = math.isfinite(value) and value > 0
        except (TypeError, ValueError):
            valid = False
        self._input.setCustomValidity("" if valid else "Enter a finite value greater than zero")  # type: ignore
        return valid and bool(self._input.checkValidity())  # type: ignore

    def invalid_input(self):
        self._input.setCustomValidity(f"Enter a positive finite value with maximum decimal precision of {self._resolution}")  # type: ignore

    @property
    def is_valid(self) -> bool:
        return self.validate()

    @property
    def value(self) -> float:
        v = float(str(self._input.value))
        if self._units.options.selected == self._inch:
            return 25.4 * v
        return v

    @property
    def stripped_value(self) -> float:
        v = float(str(self._input.value).strip())
        if self._units.options.selected == self._inch:
            return 25.4 * v
        return v

    @value.setter
    def value(self, v: float):
        if self._units.options.selected == self._inch:
            v /= 25.4
        self._input.value = f"{v:.{self._resolution}f}"

    def _get_input(self) -> web.input_:
        return self._input


class CheckboxElement(Element):
    def __init__(self, web_element: web.ElementCollection) -> None:
        super().__init__(web_element)

    @property
    def checked(self) -> bool:
        if hasattr(self._web_element, "checked"):
            return bool(self._web_element.checked)
        return False

    @checked.setter
    def checked(self, value: bool):
        if value:
            self._web_element.checked = True
        else:
            self._web_element.removeAttribute("checked")  # type: ignore
