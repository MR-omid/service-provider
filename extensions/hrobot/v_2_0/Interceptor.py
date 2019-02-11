from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo


class Interceptor(QWebEngineUrlRequestInterceptor):

    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        print('intercept:', info.requestUrl())
        if any(url in info.requestUrl().toString() for url in ['doubleclick.net','google.com/recaptcha/api2/anchor']):
            info.block(True)
