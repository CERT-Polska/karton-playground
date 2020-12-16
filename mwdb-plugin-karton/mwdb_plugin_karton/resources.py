from flask import request
from flask_restful import Resource

from werkzeug.exceptions import NotFound

from mwdb.model import Object, File
from mwdb.resources import requires_capabilities, requires_authorization
from typing import Tuple, Dict, Any

from .karton import get_karton_analysis, send_file_to_karton


class KartonCapabilities(object):
    karton_manage = "karton_manage"


class KartonAnalysisResource(Resource):
    @requires_authorization
    def get(self, identifier: str) -> Tuple[Dict[str, Any], int]:
        db_object = Object.access(identifier)
        if db_object is None:
            raise NotFound("Object not found")
        root_uid = request.args.get("root_uid")
        analysis = get_karton_analysis(db_object, root_uid)

        if analysis is None:
            return {"status": "finished"}, 200
        else:
            queues = {
                queue_name: {
                    "received_from": list(set(
                        task.headers["origin"] for task in queue.pending_tasks
                    )),
                    "status": list(set(
                        task.status for task in queue.pending_tasks
                    ))
                }
                for queue_name, queue in analysis.pending_queues.items()
            }
            return {
                "status": "running",
                "last_update": analysis.last_update,
                "processing_in": queues
            }, 200

    @requires_authorization
    @requires_capabilities(KartonCapabilities.karton_manage)
    def post(self, identifier: str) -> Tuple[Dict[str, Any], int]:
        db_file = File.access(identifier)
        if db_file is None:
            raise NotFound("Object not found or is not a file")
        root_uid = send_file_to_karton(db_file)
        return {"uid": root_uid}, 200
