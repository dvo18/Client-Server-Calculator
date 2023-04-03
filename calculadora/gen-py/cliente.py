from calculadora import Calculadora
from calculadora.ttypes import Param, Trig
from decimal import Decimal, ROUND_HALF_UP
import sys
import numpy as np
import json

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import tkinter as tk


def r(p):
    if p.f !=None: return round(p.f,3) if p.f!=round(p.f) else int(p.f)
    elif p.v !=None: return [ round(x,3) if x!=round(x) else int(x) for x in p.v ]
    else: return [ [ round(c,3) if c!=round(c) else int(c) for c in f ] for f in p.m ]

"""
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
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.master.title("Ejemplo de Interfaz")
        self.master.geometry("600x400")

        self.textbox = tk.Entry(self.master, width=50)
        self.textbox.pack(pady=10)

        self.calculate_button = tk.Button(self.master, text="Calcular", command=self.calculate)
        self.calculate_button.pack()

        self.result_label = tk.Label(self.master, text="")
        self.result_label.pack(pady=10)

        self.message_list = tk.Listbox(self.master)
        self.message_list.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.server_list = tk.Listbox(self.master, width=15)
        self.server_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_list.insert(tk.END, "Servidor")
        self.client_list = tk.Listbox(self.master, width=15)
        self.client_list.pack(side=tk.LEFT, fill=tk.Y)
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

        text = self.textbox.get()

        try:
            result = self.do_calculation(text)
            if result.f==None and result.v==None and result.m==None: raise ValueError
        except ValueError: self.result_label.config(text="---la operación no se ha realizado correctamente---")
        else: self.result_label.config(text=json.dumps(r(result)))

        message = self.get_message()
        if message:
            self.message_list.insert(tk.END, message)


    def convertir_text(self,text):
        try: return float(text)
        except ValueError: pass

        try:
            lista = eval(text)
            # Si la lista no es de tipo list, la convertimos a una lista
            if type(lista) != list: lista = [lista]
            # Si la lista contiene elementos que no son números, se levanta una excepción
            for elemento in lista: 
                if type(elemento) not in [int, float]: raise ValueError("La lista contiene elementos que no son números.")
            return lista
        except (NameError, SyntaxError): pass
        
        try:
            matriz = eval(text)
            # Verificamos que la matriz es de tipo list
            if type(matriz) != list: raise ValueError("La text no representa una matriz.")
            # Verificamos que cada fila de la matriz es de tipo list y contiene sólo números
            for fila in matriz:
                if type(fila) != list: raise ValueError("La text no representa una matriz.")
                for elemento in fila:
                    if type(elemento) not in [int, float]: raise ValueError("La matriz contiene elementos que no son números.")
            return matriz
        except (NameError, SyntaxError): pass
        
        # Si no se pudo convertir la text a ninguno de los tipos esperados, se levanta una excepción
        raise ValueError("La text no representa ningún tipo de dato válido (float, lista o matriz).")


    def do_calculation(self, text):
        try:
            texto = text.replace(" ","")

            if '+' in texto: operador='+'
            elif '-' in texto: operador='-'
            elif '*' in texto: operador='*'
            elif '/' in texto: operador='/'
            elif 'x' in texto: operador='x'
            # else: raise ValueError("---operador")

            operandos = texto.split(operador)

            parametros = [self.convertir_text(operandos[0]),self.convertir_text(operandos[1])]

            p1 = Param()
            p2 = Param()
            res = Param()
            
            if isinstance(parametros[0],float): p1.f = parametros[0]
            elif isinstance(parametros[0],list) and not isinstance(parametros[0][0],list): p1.v = parametros[0]
            elif isinstance(parametros[0],float) and isinstance(parametros[0][0],list): p1.m = parametros[0]
            # else: 

            if isinstance(parametros[1],float): p2.f = parametros[1]
            elif isinstance(parametros[1],list) and not isinstance(parametros[1][0],list): p2.v = parametros[1]
            elif isinstance(parametros[1],float) and isinstance(parametros[1][0],list): p2.m = parametros[1]
            # else:

            if operador == '+': res = self.client.suma(p1,p2)
            elif operador == '-': res = self.client.resta(p1,p2)
            elif operador == '*': res = self.client.multiplicacion(p1,p2,False)
            elif operador == '/': res = self.client.division(p1,p2)
            elif operador == 'x': res = self.client.multiplicacion(p1,p2,True)
            # else: 

            return res
        
        except ValueError: return "---la operación no se ha realizado correctamente---"


    def get_message(self):
        try:
            return self.client.getWarnings()
        except ValueError: return "---****---"

root = tk.Tk()
app = App(root)
root.mainloop()