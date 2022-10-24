# Converters

Converters allow you to serialize and deserialize types. Here in an example of an int converter.

```python
# All converters inherit from `Converter[T]` where `T` is the type that they
# convert to a string and back.
class IntConverter(Converter[int]):
    def to_str(self, obj: int) -> str:
        return str(obj)

    def from_str(self, obj: str) -> int:
        return int(obj)

flare.add_converter(
    int,          # The typehint this converter is used for.
    IntConverter  # The converter class.
)
```

## Converting Subclasses

By default converters will only effect the exact type they convert. They can
also be set to convert subclasses of that type. `self.type` can be accessed to
get the type that is currently being converted.

```python
class SubclassIntConverter(Converter[int]):
    def to_string(self, obj: int) -> str:
        return str(obj) 

    def from_str(self, obj: str) -> int:
        # `self.type` is the type that is currently being converted.
        # Examples:
        # - If an int was being converted, `self.type` would be `int`.
        # - If a `hikari.Snowflake` is being converted, `self.type` would
        #   be `hikari.Snowflake`.
        return self.type(obj)


# Add the converter for type `int` and all subtypes of `int`.
flare.add_converter(
    int,
    SubclassIntConverter,
    supports_subclass=True,
)
```
