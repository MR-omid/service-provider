import os, sys

from peewee import IntegrityError, DoesNotExist

from models.queue import QueueModel

ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from PyQt5.QtCore import QObject
import dill
import pika
import time
from pika import exceptions
from dill import PicklingError, UnpicklingError

from components.utils import ApiLogging
from vendor.custom_exception import *


class PGQ(QObject):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def put(self, item, tag, priority=None):
        """
        receive  RequestObject as item and put in PGQ
        :param item: the item that should be put on queue
        :param tag: use tag as previewing inside of each item, it must be unique
        :param priority: use priority for ordering item
        :return: return True if put item on queue successfully
        """
        try:
            model = QueueModel()
            model.name = self.name
            model.data = item
            model.tag = tag
            if priority:
                model.priority = priority
            model.save()
            ApiLogging.info('add to queue')
            return True
        except IntegrityError:
            raise DatabaseError('tag is repetitive')
        except Exception:
            raise DatabaseError('can not access database')

    def get(self):
        """
        :return: return request_object instance if can get item from queue successfully
        """
        try:
            # use id and priority for ordering queue
            result = QueueModel.select().where(QueueModel.name == self.name).order_by(
                QueueModel.id, QueueModel.priority).get()
            if result:
                # delete item that get from queue
                q = QueueModel.delete().where(QueueModel.id == result.id)
                q.execute()

                return result.data
            else:

                return None
        except Exception:  # can not access database or not item found
            return None

    # use as get from queue without order by process_id
    @staticmethod
    def get_by_tag(tag):
        """
         :param item: tag for checking PGQ
         :return: return QueueModel instance if can get item from queue without order just by tag
         """
        try:
            result = QueueModel.get(QueueModel.tag == tag)
            q = QueueModel.delete().where(QueueModel.tag == tag)
            q.execute()
        except DoesNotExist:
            raise DatabaseError('tag is not found')
        except Exception:
            raise DatabaseError('can not access database')
        return result

    @staticmethod
    def clear():
        """
          return nothing, just clear PGQ
         """
        try:
            q = QueueModel.delete()
            q.execute()
        except Exception:
            raise DatabaseError('can not access database')

    @staticmethod
    def preview(tag):
        """
          :return return true, if item with tag exist in database
         """
        try:
            query = QueueModel.get(QueueModel.tag == tag)
            if query:
                return True
            else:
                return False
        except DoesNotExist:
            return False
        except Exception:
            raise DatabaseError('can not access database')


class RMQ(QObject):
    def __init__(self, name, host='127.0.0.1'):
        super().__init__()
        self.name = name
        self.host = host
        self.connection, self.channel = self.__reconnect()
        try:
            self.channel.queue_declare(queue=self.name, durable=True)
        except pika.exceptions.AMQPConnectionError:
            raise RabbitmqConnectionError('can not access to MQ')

    def put(self, item):
        """
        receive item and serialized it, then put on queue
        :param item: the item that should be put on queue
        :return: return True if put item on queue successfully
        """
        try:
            serialized_item = dill.dumps(item)
        except PicklingError:
            raise SerializedError('can not serialized request')

        attempt = 0
        # attempt two time to put serialized item on queue
        while attempt < 2:
            try:
                # use direct exchange to put on queue (address queue by name)
                self.channel.basic_publish(exchange='',

                                           routing_key=self.name,
                                           body=serialized_item,
                                           properties=pika.BasicProperties(
                                               delivery_mode=2,  # make message persistent
                                           ))
                ApiLogging.info('add to queue')
                return True
            # if something on connection goes wrong, try again
            except pika.exceptions.AMQPConnectionError:
                self.connection, self.channel = self.__reconnect()
                attempt += 1
                continue
        # after two attempt, raise error
        raise RabbitmqConnectionError('can not access to MQ')

    def get(self):
        """
        call when need to get item from queue
        :return: return item if get item from queue successfully
        """
        attempt = 0
        # attempt two time to get item from queue
        while attempt < 2:
            try:
                # get number of item that exist on queue
                status = self.channel.queue_declare(queue=self.name, durable=True)
                if int(status.method.message_count) == 0:
                    return None
                else:
                    _, _, serialized_item = self.channel.basic_get(queue=self.name, no_ack=True)
                    if serialized_item:
                        try:
                            item = dill.loads(serialized_item)
                        except UnpicklingError:
                            raise DeSerializedError('can not de serialized item')
                        return item
                    else:
                        return None
            # if something on connection goes wrong, try again
            except pika.exceptions.AMQPConnectionError:
                self.connection, self.channel = self.__reconnect()
                attempt += 1
                continue
        # after two attempt, raise error
        raise RabbitmqConnectionError('can not access to MQ')

    def __reconnect(self):
        """
        call when need to establish new connection to MQ server
        :return: fresh channel and connection
        """
        attempt = 0
        while attempt < 3:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
                channel = connection.channel()
                return connection, channel
            except pika.exceptions.AMQPConnectionError:
                time.sleep(5)
                attempt += 1
                continue
        raise RabbitmqConnectionError('can not access MQ')
