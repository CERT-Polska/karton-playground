import logging
from mwdb.core.plugins import PluginAppContext
from mwdb.model import db, MetakeyDefinition, Group

from .karton import KartonDispatcher
from .resources import KartonAnalysisResource, KartonCapabilities

__author__ = "CERT Polska"
__version__ = "1.0.0"
__doc__ = "Karton integration plugin for MWDB"

logger = logging.getLogger("mwdb.plugin.karton")


def __plugin_entrypoint__(app_context: PluginAppContext):
    app_context.register_resource(KartonAnalysisResource, "/karton/<hash64:identifier>")
    app_context.register_hook_handler(KartonDispatcher)


def __plugin_configure__():
    logger.info("Configuring 'karton' attribute key.")
    attribute = MetakeyDefinition(key="karton",
                                  url_template="",
                                  label="Karton analysis",
                                  description="Reference to the Karton analysis for object")
    db.session.merge(attribute)
    db.session.commit()

    logger.info("Updating permissions for admin account.")
    admin_group = Group.get_by_name("admin")
    if KartonCapabilities.karton_manage not in admin_group.capabilities:
        admin_group.capabilities.append(KartonCapabilities.karton_manage)
    db.session.commit()
