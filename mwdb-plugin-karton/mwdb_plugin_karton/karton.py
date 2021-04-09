import shutil
import tempfile
from typing import Optional

from flask import g

from mwdb.core import log
from mwdb.model import Config, File, Object
from mwdb.core.plugins import PluginHookHandler

from karton.core import Config as KartonConfig, Producer, Task, Resource
from karton.core.backend import KartonBackend
from karton.core.inspect import KartonState, KartonAnalysis
from karton.core.task import TaskPriority

from .config import config

logger = log.getLogger()


def send_file_to_karton(file: File) -> str:
    try:
        path = file.get_path()
        tmpfile = None
    except Exception:
        # If get_path doesn't work: download content to NamedTemporaryFile
        # It won't work if we use S3 storage and try to reanalyze
        # existing file (not uploaded within the same request).
        tmpfile = tempfile.NamedTemporaryFile()
        file_stream = file.open()
        shutil.copyfileobj(file_stream, tmpfile)
        File.close(file_stream)
        path = tmpfile.name

    producer = Producer(
        identity="karton.mwdb",
        config=KartonConfig(config.karton.config_path)
    )

    feed_quality = g.auth_user.feed_quality
    task_priority = TaskPriority.NORMAL if feed_quality == "high" else TaskPriority.LOW
    task = Task(
        headers={
            "type": "sample",
            "kind": "raw",
            "quality": feed_quality
        },
        payload={
            "sample": Resource(file.file_name, path=path, sha256=file.sha256),
            "attributes": file.get_metakeys(as_dict=True, check_permissions=False)
        },
        priority=task_priority
    )
    producer.send_task(task)

    if tmpfile is not None:
        tmpfile.close()

    file.add_metakey("karton", task.root_uid, check_permissions=False)
    logger.info("File sent to karton with %s", task.root_uid)
    return task.root_uid


def send_config_to_karton(cfg: Config) -> str:
    producer = Producer(
        identity="karton.mwdb",
        config=KartonConfig(config.karton.config_path)
    )

    task = Task(
        headers={
            "type": "config",
            "kind": cfg.config_type,
            "family": cfg.family
        }, payload={
            "config": cfg.cfg,
            "dhash": cfg.dhash,
            "attributes": cfg.get_metakeys(as_dict=True, check_permissions=False)
        }
    )
    producer.send_task(task)
    cfg.add_metakey("karton", task.root_uid, check_permissions=False)
    logger.info("Configuration sent to karton with %s", task.root_uid)
    return task.root_uid


class KartonDispatcher(PluginHookHandler):
    def on_created_file(self, file: File) -> None:
        metakeys = file.get_metakeys(as_dict=True, check_permissions=False)
        if "karton" in metakeys:
            logger.info("Analyzed artifact - not sending to karton")
            return
        send_file_to_karton(file)

    def on_created_config(self, cfg: Config) -> None:
        metakeys = cfg.get_metakeys(as_dict=True, check_permissions=False)
        if "karton" in metakeys:
            logger.info("Analyzed artifact - not sending to karton")
            return
        send_config_to_karton(cfg)


def get_karton_analysis(db_object: Object, root_uid: Optional[str] = None) -> Optional[KartonAnalysis]:
    # Includes 'karton' permission check
    metakeys = db_object.get_metakeys(as_dict=True)

    if "karton" not in metakeys:
        return None
    if not root_uid:
        # Metakeys are ordered from oldest to latest one
        root_uid = metakeys["karton"][-1]
    elif root_uid not in metakeys["karton"]:
        # root_uid must occur in attributes to get the analysis status
        return None

    karton_config = KartonConfig(config.karton.config_path)
    karton_backend = KartonBackend(karton_config)
    karton_state = KartonState(karton_backend)

    if root_uid not in karton_state.analyses:
        return None

    if karton_state.analyses[root_uid].is_done:
        return None

    return karton_state.analyses[root_uid]
