from calculadora import Calculadora
from calculadora.ttypes import Param, Trig
from decimal import Decimal, ROUND_HALF_UP
import sys

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import tkinter as tk

"""
prodVec = True

def r(p):
    if p.f !=None: return round(p.f,3) if p.f!=round(p.f) else int(p.f)
    elif p.v !=None: return [ round(x,3) if x!=round(x) else int(x) for x in p.v ]
    else: return [ [ round(c,3) if c!=round(c) else int(c) for c in f ] for f in p.m ]

transport = TSocket.TSocket("localhost", 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = Calculadora.Client(protocol)

transport.open()

print("hacemos ping al server")
client.ping()

p1 = Param(m=[[1,3],[4,5],[6,9]])
p2 = Param(m=[[1,2],[3,4]])

try:
    resultado = client.division(p1,p2)
    if resultado.f==None and resultado.v==None and resultado.m==None: raise ValueError
except ValueError:
    print("---la operación no se ha realizado correctamente---")
    sys.exit
else:
    print(r(resultado))

transport.close()
"""

class App:
    def __init__(self,master):
        # Crear ventana principal
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.master.title("Ejemplo de Interfaz")
        self.master.geometry("600x400")

        # Crear cuadro de texto
        self.textbox = tk.Entry(self.master, width=50)
        self.textbox.pack(pady=10)

        # Crear botón de cálculo
        self.calculate_button = tk.Button(self.master, text="Calcular", command=self.calculate)
        self.calculate_button.pack()

        # Crear etiqueta para resultado
        self.result_label = tk.Label(self.master, text="")
        self.result_label.pack(pady=10)

        # Crear lista de mensajes
        self.message_list = tk.Listbox(self.master)
        self.message_list.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Crear columnas de servidor y cliente
        self.server_list = tk.Listbox(self.master, width=15)
        self.server_list.pack(side=tk.LEFT, fill=tk.Y)
        self.server_list.insert(tk.END, "Servidor")
        self.client_list = tk.Listbox(self.master, width=15)
        self.client_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.client_list.insert(tk.END, "Cliente")

        self.transport = TSocket.TSocket("localhost", 9090)
        self.transport = TTransport.TBufferedTransport(self.transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = Calculadora.Client(protocol)

        self.transport.open()

    def cerrar_ventana(self):
        self.transport.close()
        self.master.destroy()

    def calculate(self):
        self.client_list.insert(tk.END,"ping() enviado")
        self.server_list.insert(tk.END,self.client.ping())

        # Obtener texto del cuadro de texto
        text = self.textbox.get()

        # Hacer el cálculo y actualizar etiqueta de resultado
        result = self.do_calculation(text)
        self.result_label.config(text=result)

        # Agregar mensaje a lista de mensajes
        message = self.get_message()
        if message:
            self.message_list.insert(tk.END, message)


    def do_calculation(self, text):
        # Aquí iría el código para realizar el cálculo
        # En este ejemplo, simplemente se devuelve el texto al revés
        return text[::-1]
        # return "---la operación no se ha realizado correctamente---"


    def get_message(self):
        try:
            return self.client.getWarnings()
        except ValueError: return "---****---"

root = tk.Tk()
app = App(root)
root.mainloop()