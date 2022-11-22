import logging

from decouple import Csv, config as _config, undefined

logger = logging.getLogger(__name__)


def config(option: str, default=undefined, *args, **kwargs):
    """
    Pull a config parameter from the environment.

    Read the config variable ``option``. If it's optional, use the ``default`` value.
    Input is automatically cast to the correct type, where the type is derived from the
    default value if possible.

    Pass ``split=True`` to split the comma-separated input into a list.
    """
    if "split" in kwargs:
        kwargs.pop("split")
        kwargs["cast"] = Csv()
        if isinstance(default, list):
            default = ",".join(default)

    if default is not undefined and default is not None:
        kwargs.setdefault("cast", type(default))
    return _config(option, default=default, *args, **kwargs)
