import json
import logging

from ssc2ce.common.utils import hide_secret
from ssc2ce.deribit.icontroller import IDeribitController
from ssc2ce.deribit.iparser import IDeribitParser


class DeribitParser(IDeribitParser):
    """

    """
    def __init__(self, controller: IDeribitController):
        self.logger = logging.getLogger(__name__)
        self.controller = controller

    async def handle_message(self, message):
        data = json.loads(message)
        self.logger.info(f"handling:{repr(hide_secret(data))}")

        if "method" in data:
            await self.controller.handle_method_message(data)
        else:
            if "id" in data:
                if "error" in data:
                    await self.controller.handle_error(data)
                else:
                    request_id = data["id"]
                    if request_id:
                        await self.controller.handle_response(request_id, data)
            else:
                self.logger.warning(f"Unsupported message {message}")