from __future__ import annotations

import abc
import typing as t

import hikari
import hikari.api
import hikari.api.special_endpoints
from typing_extensions import Self

from flare import dataclass
from flare.components.base import CallbackComponent
from flare.components.functional import FunctionalComponent
from flare.exceptions import ComponentError

__all__: t.Final[t.Sequence[str]] = (
    "TextSelect",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ChannelSelect",
    "text_select",
    "user_select",
    "role_select",
    "mentionable_select",
    "channel_select",
)

P = t.ParamSpec("P")
T = t.TypeVar("T", bound=t.Any)


class _AbstractSelect(CallbackComponent, abc.ABC):
    """Abstract class for all select menu types."""

    __min_values: t.ClassVar[int | None]
    __max_values: t.ClassVar[int | None]
    __placeholder: t.ClassVar[hikari.UndefinedOr[str]]
    __disabled: t.ClassVar[bool | None]

    def __init_subclass__(
        cls,
        cookie: str | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(cookie, _dataclass_fields)
        cls.__min_values = min_values
        cls.__max_values = max_values
        cls.__placeholder = placeholder
        cls.__disabled = disabled

    def __post_init__(self):
        super().__post_init__()
        self.min_values = self.__min_values
        self.max_values = self.__max_values
        self.placeholder = self.__placeholder
        self.disabled = self.__disabled

    @property
    @abc.abstractmethod
    def _component_type(self) -> hikari.ComponentType:
        ...

    @property
    def width(self) -> int:
        return 5

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

    def build(self, action_row: hikari.api.MessageActionRowBuilder) -> hikari.api.SelectMenuBuilder[t.Any]:
        """
        Build the select menu into the passed in action row.
        """
        select = action_row.add_select_menu(self._component_type, self.custom_id)

        if self.placeholder and len(self.placeholder) > 100:
            raise ComponentError("Placeholder text must be shorter than 100 characters.")

        if self.min_values:
            select.set_min_values(self.min_values)
        if self.max_values:
            select.set_max_values(self.max_values)
        if self.disabled:
            select.set_is_disabled(self.disabled)
        select.set_placeholder(self.placeholder)
        select.add_to_container()

        return select


class TextSelect(_AbstractSelect):
    """
    Class for a select menu message component.

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

    __options: t.ClassVar[t.Sequence[tuple[str, str] | str | hikari.SelectMenuOption] | None]

    def __init_subclass__(
        cls,
        cookie: str | None = None,
        options: t.Sequence[tuple[str, str] | str | hikari.SelectMenuOption] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(
            cookie=cookie,
            min_values=min_values,
            max_values=max_values,
            placeholder=placeholder,
            disabled=disabled,
            _dataclass_fields=_dataclass_fields,
        )
        cls.__options = options

    def __post_init__(self):
        super().__post_init__()
        self.options = self.__options

    def set_options(self, *options: tuple[str, str] | str | hikari.SelectMenuOption) -> Self:
        self.options = options
        return self

    @property
    def _component_type(self) -> hikari.ComponentType:
        return hikari.ComponentType.TEXT_SELECT_MENU

    def build(
        self, action_row: hikari.api.MessageActionRowBuilder
    ) -> hikari.api.special_endpoints.TextSelectMenuBuilder[t.Any]:
        select: hikari.api.special_endpoints.TextSelectMenuBuilder[t.Any] = super().build(action_row)  # type: ignore

        if self.options:
            if len(self.options) > 25:
                raise ComponentError("Cannot create a select menu with more than 25 options.")

            if self.min_values and self.min_values > len(self.options):
                raise ComponentError("Cannot create a select menu with greater min options than options.")

            if self.max_values and self.max_values > len(self.options):
                raise ComponentError("Cannot create a select menu with greater max options than options.")

            for option in self.options:
                if isinstance(option, str):
                    select.add_option(option, option).add_to_menu()
                elif isinstance(option, hikari.SelectMenuOption):
                    opt = select.add_option(option.label, option.value)
                    if option.description:
                        opt.set_description(option.description)
                    if option.emoji:
                        opt.set_emoji(option.emoji)
                    if option.is_default:
                        opt.set_is_default(option.is_default)
                    opt.add_to_menu()
                else:
                    select.add_option(*option).add_to_menu()
        else:
            raise ComponentError("Expected one or more options for select menu. Got zero.")

        return select


class UserSelect(_AbstractSelect):
    """
    Class for a user select menu message component.

    Args:
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

    @property
    def _component_type(self) -> hikari.ComponentType:
        return hikari.ComponentType.USER_SELECT_MENU


class RoleSelect(_AbstractSelect):
    """
    Class for a role select menu message component.

    Args:
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

    @property
    def _component_type(self) -> hikari.ComponentType:
        return hikari.ComponentType.ROLE_SELECT_MENU


class MentionableSelect(_AbstractSelect):
    """
    Class for a mentionable select menu message component.

    Args:
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

    @property
    def _component_type(self) -> hikari.ComponentType:
        return hikari.ComponentType.MENTIONABLE_SELECT_MENU


class ChannelSelect(_AbstractSelect):
    """
    Class for a channel select menu message component.

    Args:
        channel_types:
            The channel types that will appear in this select menu.
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

    __channel_types: t.ClassVar[t.Sequence[hikari.ChannelType] | None]

    def __init_subclass__(
        cls,
        cookie: str | None = None,
        channel_types: t.Sequence[hikari.ChannelType] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(
            cookie=cookie,
            min_values=min_values,
            max_values=max_values,
            placeholder=placeholder,
            disabled=disabled,
            _dataclass_fields=_dataclass_fields,
        )
        cls.__channel_types = channel_types

    def __post_init__(self):
        super().__post_init__()
        self.channel_types = self.__channel_types

    def set_channel_types(self, *channel_types: hikari.ChannelType) -> Self:
        self.channel_types = channel_types
        return self

    def build(
        self, action_row: hikari.api.MessageActionRowBuilder
    ) -> hikari.api.special_endpoints.ChannelSelectMenuBuilder[t.Any]:
        select: hikari.api.special_endpoints.ChannelSelectMenuBuilder[t.Any] = super().build(action_row)  # type: ignore

        if self.channel_types:
            select.set_channel_types(self.channel_types)

        return select

    @property
    def _component_type(self) -> hikari.ComponentType:
        return hikari.ComponentType.CHANNEL_SELECT_MENU


class _AbstractSelectFunction(FunctionalComponent[T], abc.ABC):
    """
    A decorator to create a `flare.Select`. This is a shorthand for when type
    safety is not needed.
    """

    def __init__(
        self,
        *,
        cookie: str | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
    ) -> None:
        self.cookie = cookie
        self.min_values = min_values
        self.max_values = max_values
        self.placeholder = placeholder
        self.disabled = disabled

    @property
    @abc.abstractmethod
    def component_type(self) -> type[T]:
        return TextSelect

    @property
    def kwargs(self) -> dict[str, t.Any]:
        return {
            "cookie": self.cookie,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "placeholder": self.placeholder,
            "disabled": self.disabled,
        }


class text_select(_AbstractSelectFunction[TextSelect]):
    def __init__(
        self,
        *,
        cookie: str | None = None,
        options: t.Sequence[tuple[str, str] | str | hikari.SelectMenuOption] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
    ) -> None:
        self.options = options
        super().__init__(
            cookie=cookie,
            min_values=min_values,
            max_values=max_values,
            placeholder=placeholder,
            disabled=disabled,
        )

    @property
    def component_type(self) -> type[TextSelect]:
        return TextSelect

    @property
    def kwargs(self) -> dict[str, t.Any]:
        kwargs = super().kwargs
        kwargs["options"] = self.options
        return kwargs


class user_select(_AbstractSelectFunction[UserSelect]):
    @property
    def component_type(self) -> type[UserSelect]:
        return UserSelect


class role_select(_AbstractSelectFunction[RoleSelect]):
    @property
    def component_type(self) -> type[RoleSelect]:
        return RoleSelect


class mentionable_select(_AbstractSelectFunction[MentionableSelect]):
    @property
    def component_type(self) -> type[MentionableSelect]:
        return MentionableSelect


class channel_select(_AbstractSelectFunction[ChannelSelect]):
    def __init__(
        self,
        *,
        cookie: str | None = None,
        channel_types: t.Sequence[hikari.ChannelType] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
    ) -> None:
        self.channel_types = channel_types
        super().__init__(
            cookie=cookie,
            min_values=min_values,
            max_values=max_values,
            placeholder=placeholder,
            disabled=disabled,
        )

    @property
    def component_type(self) -> type[ChannelSelect]:
        return ChannelSelect

    @property
    def kwargs(self) -> dict[str, t.Any]:
        kwargs = super().kwargs
        kwargs["channel_types"] = self.channel_types
        return kwargs


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
