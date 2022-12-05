from __future__ import annotations

import typing as t

import hikari
from typing_extensions import Self

from flare import dataclass
from flare.components.base import CallbackComponent
from flare.components.functional import FunctionalComponent
from flare.exceptions import ComponentError

__all__: t.Final[t.Sequence[str]] = ("Select", "select")

P = t.ParamSpec("P")


class Select(CallbackComponent):
    """
    Decorator for a select menu message component.

    Args:
        options:
            An array of options for the select menu. This must be provided when
            the class is created or using `Select.set_options`.
        min_vales:
            The minimum amount of values a user must select.
        max_values:
            The maximum amount of values a user must select.
        placeholder:
            Placeholder text when no option is selected.
        disabled:
            Whether the button is disabled.
        cookie:
            An identifier to use for the select menu. A custom cookie can be
            supplied so a shorter one is used in serializing and deserializing.
    """

    __options: t.Sequence[tuple[str, str] | str] | None
    __min_values: int | None
    __max_values: int | None
    __placeholder: hikari.UndefinedOr[str]
    __disabled: bool | None

    def __init_subclass__(
        cls,
        cookie: str | None,
        options: t.Sequence[tuple[str, str] | str] | None,
        min_values: int | None,
        max_values: int | None,
        placeholder: hikari.UndefinedOr[str],
        disabled: bool | None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(cookie, _dataclass_fields)
        cls.__options = options
        cls.__min_values = min_values
        cls.__max_values = max_values
        cls.__placeholder = placeholder
        cls.__disabled = disabled

    def __post_init__(self):
        super().__post_init__()
        self.options = self.__options
        self.min_values = self.__min_values
        self.max_values = self.__max_values
        self.placeholder = self.__placeholder
        self.disabled = self.__disabled

    @property
    def width(self) -> int:
        return 5

    def set_options(self, *options: tuple[str, str] | str) -> Self:
        self.options = options
        return self

    def set_min_values(self, min_values: int | None) -> Self:
        self.min_values = min_values
        return self

    def set_max_values(self, max_values: int | None) -> Self:
        self.max_values = max_values
        return self

    def set_placeholder(self, placeholder: hikari.UndefinedOr[str]) -> Self:
        self.placeholder = placeholder
        return self

    def set_disabled(self, disabled: bool) -> Self:
        self.disabled = disabled
        return self

    def build(self, action_row: hikari.api.MessageActionRowBuilder) -> None:
        """
        Build the select menu into the passed in action row.
        """
        select = action_row.add_select_menu(self.custom_id)

        if self.options:
            for option in self.options:
                if isinstance(option, str):
                    select.add_option(option, option).add_to_menu()
                else:
                    select.add_option(*option).add_to_menu()
        else:
            raise ComponentError("Expected one or more options for select menu. Got zero.")

        if len(self.options) > 25:
            raise ComponentError("Cannot create a select menu with more than 25 options.")

        if self.placeholder and len(self.placeholder) > 100:
            raise ComponentError("Placeholder text must be shorter than 100 characters.")

        if self.min_values and self.min_values > len(self.options):
            raise ComponentError("Cannot create a select menu with greater min options than options.")

        if self.max_values and self.max_values > len(self.options):
            raise ComponentError("Cannot create a select menu with greater max options than options.")

        if self.min_values:
            select.set_min_values(self.min_values)
        if self.max_values:
            select.set_max_values(self.max_values)
        if self.disabled:
            select.set_is_disabled(self.disabled)
        select.set_placeholder(self.placeholder)
        select.add_to_container()


class select(FunctionalComponent[Select]):
    """
    A decorator to create a `flare.Select`. This is a shorthand for when type
    safety is not needed.
    """

    def __init__(
        self,
        *,
        cookie: str | None = None,
        options: t.Sequence[tuple[str, str] | str] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
    ) -> None:
        self.cookie = cookie
        self.options = options
        self.min_values = min_values
        self.max_values = max_values
        self.placeholder = placeholder
        self.disabled = disabled

    @property
    def component_type(self) -> type[Select]:
        return Select

    @property
    def kwargs(self) -> dict[str, t.Any]:
        return {
            "cookie": self.cookie,
            "options": self.options,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "placeholder": self.placeholder,
            "disabled": self.disabled,
        }


# MIT License
#
# Copyright (c) 2022-present Lunarmagpie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
