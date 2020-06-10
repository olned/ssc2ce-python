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
        self.on_before_handling = None

    async def handle_message(self, message):
        if self.on_before_handling:
            self.on_before_handling(message)

        data = json.loads(message)

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
            elif self.on_before_handling is not None:
                self.logger.warning(f"Unsupported message {message}")
