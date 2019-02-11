import base64
import uuid
from components.utils import gzip_compress, gzip_decompress
from PyQt5 import QtNetwork
from PyQt5.QtCore import QThreadPool, QRunnable, QByteArray
from PyQt5.QtNetwork import QTcpServer, QHostAddress

from components import utils
from components.utils import ApiLogging
from core.command import Command
from core.queue import PGQ

from models.module import ModuleModel


class RequestObject(object):
    def __init__(self, route, call_back, token, process_id, data, module_version):
        self.route = route
        self.call_back = call_back
        self.token = token
        self.process_id = process_id
        self.data = data
        self.module_version = module_version


class Handler(QRunnable):
    """ handle incoming connection, get data from client, extract information and add to queue """

    def __init__(self, socketDescriptor, queues):
        super().__init__()
        self.socketDescriptor = socketDescriptor
        self.size = None
        self.priority = None
        self.timeout = None
        self.route_name = None
        self.route_code = None
        self.route = None
        self.call_back = None
        self.token = None
        self.module_version = None
        self.buffer = QByteArray()
        self.tcpSocket = None
        self.queues = queues

    def run(self):
        """ create new socket for communicate with client, receive header data contain request information, process it and
            send accept, then listen for receive body data
        """

        self.tcpSocket = QtNetwork.QTcpSocket()
        if not self.tcpSocket.setSocketDescriptor(self.socketDescriptor):
            raise Exception(self.tcpSocket.errorString())
        self.tcpSocket.waitForReadyRead()
        buffer = self.tcpSocket.readAll()

        try:
            try:
                self.size, self.priority, self.timeout, self.route, self.module_version, self.call_back, self.token = self.extract(
                    buffer)
            except ValueError:
                self.size, self.priority, self.timeout, self.route, self.call_back, self.token = self.extract(buffer)
            self.call_back = base64.b64decode(self.call_back).decode()
            self.token = utils.decrypt_rsa(self.token, utils.get_rsa())
            self.route_name = self.route_to_name(self.route)
            ApiLogging.info('route is: ' + self.route_name)
            if not self.module_version:
                self.module_version = 'v_1_0'
        except Exception as e:
            print("rejected", e)
            self.tcpSocket.write('{"status":"reject"}'.encode())
            self.__close()
        else:
            self.size = int(self.size)
            self.tcpSocket.write('{"status":"accept"}'.encode())
            self.tcpSocket.waitForBytesWritten()
            self.tcpSocket.readyRead.connect(self.__read_data)
            self.tcpSocket.waitForDisconnected(
                30 * 60 * 1000)  # FIXME: change to better solution for big data timeout and handle incompleted data

    @staticmethod
    def extract(buffer: QByteArray) -> str:
        """ extract 'size:priority:timeout:route:call_back:token' from header """
        try:
            return buffer.data().decode().split(":")
        except ValueError:
            raise

    @staticmethod
    def route_to_name(route_code):
        try:
            result = ModuleModel.get(ModuleModel.code == route_code, ModuleModel.active == True)
            return result.alias
        except Exception:
            raise

    @staticmethod
    def route_to_group(route_name):
        try:
            result = ModuleModel.get(ModuleModel.alias == route_name)
            return result.category
        except Exception:
            return None

    def __read_data(self):
        """ slot called when data available in socket buffer for read
            after read all data, create new object contain mixed extracted header information and raw body data
            then add this new object to queue, clear buffer and close socket
        """
        if self.tcpSocket.bytesAvailable() and self.size is not None:
            self.buffer.append(self.tcpSocket.readAll())
        if self.size is not None and self.size == self.buffer.size():
            data = self.buffer.data()
            uncompress_data = gzip_decompress(data)
            self.buffer.clear()
            self.buffer.append(uncompress_data)
            if Command.is_action(self.route):
                try:
                    command_result = getattr(Command, self.route_name)(self.buffer.data())
                    compress_data = gzip_compress(utils.to_json({"status": command_result.get('status'),
                                   "data": command_result.get('data')}).encode())
                    self.tcpSocket.write(compress_data)
                    self.__close()
                except Exception:
                    self.__close()
                finally:
                    self.buffer.clear()
            else:
                process_id = uuid.uuid4().hex
                request_object = RequestObject(self.route_name, self.call_back, self.token, process_id,
                                               self.buffer.data(),
                                               self.module_version)
                # TODO: add this object to RabbitMQ
                group = self.route_to_group(self.route_name)  # FIXME: route_to_group
                try:
                    if not group:
                        self.buffer.clear()
                        compress_data = gzip_compress('{"status":"failed","message":"this service is not categorized"}'.encode())
                        self.tcpSocket.write(compress_data)
                        self.__close()
                    else:
                        # print('try connect to queue')
                        self.queues.get(group).put(request_object,process_id)
                        # print(group)
                        # print('object added to queue')
                        self.buffer.clear()
                        compress_data = gzip_compress('{{"status":"success","process_id":"{0}"}}'.format(process_id).encode())
                        self.tcpSocket.write(compress_data)
                        self.__close()
                except Exception:
                    self.buffer.clear()
                    compress_data = gzip_compress('{"status":"failed","message":"Internal Server Error"}'.encode())
                    self.tcpSocket.write(compress_data)
                    self.__close()

    def __close(self):
        """ close socket connection """
        self.tcpSocket.flush()
        self.tcpSocket.close()
        self.tcpSocket.deleteLater()


class Server(QTcpServer):
    """ create tcp server and listen for new client connection
        add new connection to ThreadPool for communicate with that
    """

    def __init__(self, parent=None):
        """ initialize Queue, Manager and ThreadPool for work with that """

        super().__init__(parent)
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(5000)
        self.queues = {'HQueue': PGQ('HQueue'), 'MQueue': PGQ('MQueue'), 'LQueue': PGQ('LQueue')}

    def start(self):
        """ start listening on specific tcp ip/port and connect to TcpServer error signal """
        self.setMaxPendingConnections(5000)
        if self.listen(QHostAddress.AnyIPv4, 8001):
            print("Server: started")
        else:
            raise Exception(self.errorString())

        self.acceptError.connect(self.error)

    def incomingConnection(self, socketDescriptor: int):
        """ this method called when new connection will be  available
            initialize Handler and add it to ThreadPool
        """

        handle = Handler(socketDescriptor, self.queues)
        handle.setAutoDelete(True)
        self.pool.start(handle)

    @staticmethod
    def error(e):
        """ called with TcpServer error signal and handle received error """

        print(e.errorString())
