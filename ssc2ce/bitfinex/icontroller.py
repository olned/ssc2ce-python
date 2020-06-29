from abc import ABC, abstractmethod


class IBitfinexController(ABC):
    @abstractmethod
    def handle_pong(self, ts: int, cid: int):
        """
        handle pong response
        :return:
        """
        pass

    @abstractmethod
    def handle_version_and_status(self, version_no: int, status: int):
        """
        Handle version number and status

        After the connection is established, the server sends the version number and
        status flag status (1 for operative, 0 for maintenance)

        :param version_no:
        :param status:
        :return:
        """
        pass

    @abstractmethod
    def handle_error(self, error_code: int):
        """
        Handle error message

        :param error_code:
            10000 : Unknown event
            10001 : Unknown pair
            10011 : Unknown Book precision
            10012 : Unknown Book length
            10300 : Subscription failed (generic)
            10301 : Already subscribed
            10302 : Unknown channel
            10305 : Reached limit of open channels
            10400 : Subscription failed (generic)
            10401 : Not subscribed

        :param message:
        :return:
        """

        pass

    @abstractmethod
    def handle_info(self, info_code: int):
        """

        :param info_code:
            20051 - Stop/Restart Websocket Server (please reconnect)
            20060 - Entering in Maintenance mode. Please pause any activity and resume after
                    receiving the info message 20061 (it should take 120 seconds at most).
            20061 - Maintenance ended. You can resume normal activity. It is advised to
                    unsubscribe/subscribe again all channels.
        :return:
        """