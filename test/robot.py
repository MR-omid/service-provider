import base64
from time import sleep

from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR
print("Qt version:", QT_VERSION_STR)
print("SIP version:", SIP_VERSION_STR)
print("PyQt version:", PYQT_VERSION_STR)



from PyQt5.QtCore import QCoreApplication, QUrl, QPoint
from PyQt5.QtGui import QImage, QPainter, QPixmap, QRegion
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QApplication

app = QApplication([])

print()

Page = QWebEnginePage()
view = QWebEngineView()
Page.setView(view)
left = 91
right = 363
top = -250
bottom = -49

def p(html):
    print('html: ', html)
    b64 = html.split(',')
    if len(b64) > 1:
        img_b64 = b64[-1]
        f = open('img.png','wb')
        f.write(base64.b64decode(img_b64))
        f.close()

    Page.printToPdf('testtttt.pdf')
    print('to dpf2')


def stat(result):
    print('result is: ', result)


def t(a):
    print('status: ', a)

    # viewPage.runJavaScript('var img=document.querySelector(".captcha_render");var canvas=document.createElement("canvas");canvas.width=img.width;canvas.height=img.height;var ctx=canvas.getContext("2d");ctx.drawImage(img,0,0);var dataURL=canvas.toDataURL("image/png");dataURL;',p)
    # viewPage.runJavaScript('window.a1a = "omid";',p)
    # viewPage.runJavaScript('"hi "+a1a;',stat)
    # viewPage.printToPdf('nic.pdf')
    # viewPage.printToPdf('t11111111111.pdf')
    # size = viewPage.contentsSize().toSize()
    # image = QImage(size, QImage.Format_ARGB32)
    # region = QRegion(0,0,size.width(), size.height())
    # painter = QPainter(image)
    # viewPage.view().render(painter, QPoint(), region)
    # painter.end()
    # image.save("test.png", "PNG", 80)
    print('saved!')


Page.loadFinished.connect(t)

Page.load(QUrl('https://google.com/'))

# image = QImage(page.contentsSize(),QImage.Format_ARGB32)
# painter = QPainter(image)
# page.ren


app.exec()