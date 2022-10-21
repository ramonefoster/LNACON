import sys
import serial.tools.list_ports
from threading import Thread
from read_serial import SerialRead
from client import Client
from PyQt5 import QtWidgets, uic, QtCore, QtGui
pyQTfileName = "client.ui"
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
        menu.addAction("Parar", self.stop_all)
        self.activated.connect(self.restore_window)
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
        self.my.stop_all()

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        """UI principal"""
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # elementos UI
        listPorts = self.com_ports()
        self.box_port.clear()
        self.box_port.addItems(listPorts) 
        self.box_baud.clear() 
        list_baud = ['','2400', '4800', '9600', '19200', '115200'] 
        self.box_baud.addItems(list_baud)

        #flags, bits e threads
        self.thread_t = None
        self.is_running = False
        self.server_status = False
        self.echo = ''

        #Client
        self.client = None
        self.serial = None

        #botões
        self.btnStart.clicked.connect(self.start_read)
        self.btnStop.clicked.connect(self.stop_all)

        #timer de uso geral (1s)
        self.timer_status = QtCore.QTimer()
        self.timer_status.timeout.connect(self.check_status)
        self.timer_init()

    def show_from_tray(self):
        """Restaura a janela da tray"""
        self.show()
    
    def minimize_tray(self):
        """Minimiza para a Tray (icones ocultos da barra de ferramentas)"""
        self.hide()

    def com_ports(self):
        """Verifica e mostra as portas COM conectadas"""
        port_list = serial.tools.list_ports.comports()
        connected = [""]
        for element in port_list:
            connected.append(element.device)
        return(connected)
    
    def init_client(self):
        """Connecta o client ao servidor"""
        host = self.txt_host.text() 
        netport = self.txt_netport.text()        
        if netport.isdigit():
            self.txt_status.append("Tentando conexão: "+host)
            self.client = Client(host, netport)            
            # a função socket.connect é syncrona
            try:
                self.client.connect()
                self.server_status = True
            except Exception as e:
                self.txt_status.append("ERROR: "+str(e))
                self.server_status = False

    def start_read(self):  
        """Inicia operação
        1- Tenta conexão com o servidor
        2- inicia o trabalho"""   
        init_resp = self.init_client() 
        #printa a resposta do servidor quando conectado
        self.txt_status.append(init_resp)
        if self.server_status: 
            if self.thread_t:
                self.thread_t.join()        
            self.read_serial() 
        else:
            #seta flag e muda UI
            self.is_running = False
            self.txt_status.append(init_resp)  
            self.label_status.setStyleSheet("background-color: indianred")       

    def read_serial(self):
        """LÊ DA PORTA SERIAL"""
        com_port = self.box_port.currentText() 
        baud = self.box_baud.currentText()
        path_log = self.txt_log_path.text()
        savelog = self.check_save_log.isChecked()
        if "COM" in com_port and baud.isdigit():                
            try:
                #Inicia a class da Serial e starta o loop em uma thread separada
                self.serial = SerialRead(com_port, int(baud), path_log, savelog)                    
                self.thread_t = Thread(target=self.loop, args=[])
                self.thread_t.start()
                #Printa o nome do dispositivo conectado na USB
                device_name = self.serial.device_name()
                self.txt_info_usb.setText(device_name)                          
                #seta flag e muda UI
                self.is_running = True
                self.txt_status.append("Reading COM")                  
            except Exception as e:
                #caso falhe por qualquer motivo, printa o motivo no status
                self.is_running = False
                self.txt_status.append(str(e))                
    
    def loop(self):
        """Loop em thread separada para leitura da serial ininterrupta
        e envio via TCP para o endereço servidor, enquanto flag = True""" 
        while self.is_running:
            if self.server_status:
                echo = self.client.send(self.serial.return_data())
                print(echo)
                if type(echo, bytes):
                    echo = echo.decode('utf-8')
                self.echo = echo                              
    
    def stop_all(self):
        """Para tudo"""
        self.is_running = False
        if self.thread_t:            
            self.thread_t.join()
        if self.serial:
            self.serial.close_port()
        if self.client:
            self.client.disconnect()
        self.txt_status.append("Stopped") 
    
    def check_status(self):
        if not self.is_running:
            self.label_status.setStyleSheet("background-color: indianred")             
        else:
            self.txt_server.append(self.echo)
            self.label_status.setStyleSheet("background-color: lightgreen") 
            if "timeout" in self.echo:
                #tenta reconectar se timeout:
                self.client.connect()
            
    
    def closeEvent(self, event):
        """Close application"""         
        self.stop_all()               
        event.accept()
    
    def timer_init(self):
        """atualiza elementos UI de 1 em 1 segundo"""
        self.timer_status.start(1000)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon('opd.ico'), w)
    trayIcon.show()
    
    window.show()
    sys.exit(app.exec_())
