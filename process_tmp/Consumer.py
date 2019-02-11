import pika


# import dill
from components.utils import ApiLogging
from process_tmp import config


class Consumer:
    # declare connection and channel to rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.SERVER_ADDRESS))
    channel = connection.channel()

    def __init__(self, queue_name, limit):
        # declaring queue
        self.queue_name = queue_name
        # define default fetch request limit
        self.process_limit = limit

    # get message from queue
    def __get_message(self):
        # check if connection in exist
        if self.connection:
            a = self.channel.basic_get(queue=self.queue_name, no_ack=True)
            return a
        else:
            self.connection, self.channel = self.__connection()
            a = self.channel.basic_get(queue=self.queue_name, no_ack=True)
            return a

    # set new limit for accepting request from queue
    # TODO: use another way to set limit
    def __set_limit(self, limit):
        self.process_limit = limit

    # set a new connection, if the old one does not exist
    @staticmethod
    def __connection():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.SERVER_ADDRESS))
        channel = connection.channel()
        return connection, channel

    # public function run, for using this class from outside, starting to consume from queue
    def run(self):
        ApiLogging.info('Start Consuming From ' + str(self.queue_name))
        while 1:
            # # check if there is new request on queue
            status = self.channel.queue_declare(queue=self.queue_name, durable=True)
            if int(status.method.message_count) == 0:
                continue
            else:
                ApiLogging.info(status.method.message_count)
                # check if still we're able to process request, then get new message
                if int(self.process_limit) == 3:
                    (_, _, message) = self.__get_message()
                    ApiLogging.info(message)
                    # TODO: saving request on database
                    # TODO: de serializing message and sent to task
                    # request = dill.loads(message)
                    # pass request to task
