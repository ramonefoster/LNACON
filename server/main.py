import sys
from server import Server
import datetime

from PyQt5 import QtWidgets, uic, QtCore, QtGui
pyQTfileName = "server.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(pyQTfileName)

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        """Classe apenas para criação do icone e ações
        da Tray (minimizado nos icones ocultos)
        de modo que o programa rode em segundo plano"""
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)
        self.setContextMenu(menu)
        menu.addAction("Exit", self.exit)
        menu.addAction("Mostrar", self.mostrar)
        self.activated.connect(self.restore_window)
        menu.addAction("Parar", self.stop_all)
        self.my = MyApp()

    def exit(self):
        """Fecha programa pela Tray"""
        QtCore.QCoreApplication.exit()
    
    def restore_window(self, reason):
        """Restaura se icone clicado 2x"""
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.my.show()

    def mostrar(self):
        """Restaura janela"""
        self.my.show_from_tray()
    
    def stop_all(self):
        """Para o programa pelo icone da tray"""
        self.my.close_server()

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.server = None
        self.is_running = False

        #botoes
        self.btnStart.clicked.connect(self.start_server)
        self.btnStop.clicked.connect(self.close_server)
        self.btnHide.clicked.connect(self.minimize_tray)

        #timer
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.print_sysmsg)
    
    def start_timer_all(self):
        self.timer.start(800)
    
    def minimize_tray(self):
        """Minimiza para a Tray"""
        self.hide()
    
    def show_from_tray(self):
        """Restaura janela da Tray"""
        self.show()

    def start_server(self):
        """Inicia o servidor"""
        port = self.txt_netport.text()
        if port.isdigit():
            self.server = Server(int(port))            
            status = self.server.get_status()
            self.txt_host.setText(status["server"])
            hora_inicio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.txt_server.append(f"Servidor iniciado {hora_inicio}")
            self.label_status.setStyleSheet("background-color: lightgreen")
            self.start_timer_all()
    
    def print_sysmsg(self):  
        status = self.server.get_status()
        sys_msg = status["sys_msg"]
        if type(sys_msg) is bytes: 
            sys_msg = sys_msg.decode('utf-8')  
        if sys_msg:
            self.txt_server.append(sys_msg)          
        try:
            print (status["addrs"])
            self.txt_n_conn.setText(str(status["n_conn"]))
            for addr in status["addrs"]:
                self.txt_list_addr.setText(addr[0])
            if len(status["addrs"])==0:
                self.txt_list_addr.setText('')
        except Exception as e:
            self.txt_server.append(str(e))

    def close_server(self):
        self.timer.stop()
        try:
            self.server.stop_server()  
            self.label_status.setStyleSheet("background-color: indianred")
        except Exception as e:
            print(str(e))

    def closeEvent(self, event):
        """Close application"""
        self.close_server()
        event.accept()     
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon('rede.png'), w)
    trayIcon.show()
    
    window.show()
    sys.exit(app.exec_())