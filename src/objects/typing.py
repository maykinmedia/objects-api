from typing import TypeAlias

JSONPrimitive: TypeAlias = "str | int | float | bool | None"

JSONValue: TypeAlias = "JSONPrimitive | JSONObject | list[JSONValue]"

JSONObject: TypeAlias = dict[str, JSONValue]
