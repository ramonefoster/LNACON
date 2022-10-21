import serial
import serial.tools.list_ports
import threading
import os, datetime
import time

class SerialRead(threading.Thread):
    def __init__(self, porta, baud, file_path, save_log):   
        threading.Thread.__init__(self)  

        #Variaveis
        self.file_path = file_path  
        self.is_checked = save_log        
        self.stop_bit = False
        self.echo = ''

        self.ser = serial.Serial(
            port=porta,
            baudrate=baud,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            timeout=2)
        self.ser.close()
        if self.ser.is_open == False:
            try:
                self.echo = f"Openning {self.ser.name}"
                self.ser.open()
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception as e:
                print(e)
            self.t_thread = threading.Thread(target = self.read)
            self.t_thread.start()

    def return_data(self):
        return self.echo
    
    def device_name(self):
        return self.ser.name

    def read(self):
        while (True):   
            data_str = ''         
            resp = self.ser.in_waiting
            if self.stop_bit:
                time.sleep(1)
                break
            if (resp > 0):
                t0 = time.time()
                while (not "\n" in data_str):
                    data_str += self.ser.read().decode()
                    if (time.time() - t0) > self.time_out_dome:
                        self.ser.reset_input_buffer()
                        self.ser.reset_output_buffer()
                        self.returned_data = "Timeout"
                        break
                hours = datetime.datetime.now().strftime("%H")
                minute = datetime.datetime.now().strftime("%M")
                seconds = datetime.datetime.now().strftime("%S")
                time_log = str(hours) + ":" + str(minute) + ":" + str(seconds)
                self.echo = data_str
                if self.is_checked and os.path.exists(self.file_path):
                    with open(self.file_path, 'a+') as datafile:
                        datafile.write(time_log+' - '+data_str)
                        datafile.write("\n")
            time.sleep(.1)
    
    def close_port(self):
        self.stop_bit = True
        self.t_thread.join()
        self.ser.close()
        



