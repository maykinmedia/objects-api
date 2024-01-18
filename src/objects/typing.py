from typing import Union

JSONPrimitive = Union[str, int, None, float, bool]

JSONValue = Union[JSONPrimitive, "JSONObject", list["JSONValue"]]

JSONObject = dict[str, JSONValue]
