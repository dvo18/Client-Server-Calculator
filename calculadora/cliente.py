from calculadora import Calculadora
from calculadora.ttypes import Param, Trig, Op
from decimal import Decimal, ROUND_HALF_UP
import sys
import numpy as np
import json

from colored import stylize

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import tkinter as tk


def r(p):
    if p.f !=None: return round(p.f,3) if p.f!=round(p.f) else int(p.f)
    elif p.v !=None: return [ round(x,3) if x!=round(x) else int(x) for x in p.v ]
    else: return [ [ round(c,3) if c!=round(c) else int(c) for c in f ] for f in p.m ]


class App:
    def __init__(self,master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.master.title("Ejemplo de Interfaz")
        self.master.geometry("500x550")

        self.textbox = tk.Entry(self.master, width=50)
        self.textbox.pack(pady=10)

        self.calculate_button = tk.Button(self.master, text="Calcular", command=self.calculate)
        self.calculate_button.pack()

        self.clear_button = tk.Button(self.master, text="Limpiar", command=self.clear_textboxes)
        self.clear_button.pack()

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


    def clear_textboxes(self):
        self.server_list.delete(0, tk.END)
        self.server_list.insert(tk.END, "Servidor")
        self.client_list.delete(0, tk.END)
        self.client_list.insert(tk.END, "Cliente")
        self.message_list.delete(0, tk.END)


    def calculate(self):
        self.client_list.insert(tk.END,"ping() enviado")

        text = self.textbox.get()

        if text:
            self.server_list.insert(tk.END,self.client.ping())
            try:
                result = self.calcular(text)
                if result != None:
                    if result.f==None and result.v==None and result.m==None: raise ValueError
                    else: self.result_label.config(text=json.dumps(r(result)))
                else: raise ValueError
            except ValueError: self.result_label.config(text="---la operación no se ha realizado correctamente---")

            message = self.get_message()
            for i in range(len(message)):
                if "error" in message[i]: color = "red3"
                elif "warning" in message[i]: color = "orange2"
                else: color = "black"

                self.message_list.insert(tk.END, message[i])
                self.message_list.itemconfigure(self.message_list.size()-1, fg=color)


    def convertir_text(self,text):
        try:
            if not "[[" in text and not "[" in text: return float(text)
            elif not "[[" in text: return [ float(num) for num in text.strip('[]').split(',') ]
            elif "[[" in text: return [ [ float(num) for num in fila.strip('[]').split(',') ] for fila in text.strip('[]').split('],[') ]
            else: raise ValueError
        except ValueError: 
            print("La text no representa ningún tipo de dato válido (float, lista o matriz).")
            return None


    def calcular(self, text):
        try:
            texto = text.replace(" ","")
            oper = Op()

            if '+' in texto: oper = Op.SUMA
            elif '-' in texto: oper = Op.RESTA
            elif '*' in texto: oper = Op.MULTIPLICACION
            elif '/' in texto: oper = Op.DIVISION
            elif 'x' in texto: oper = Op.PROD_ESCALAR
            elif '^' in texto: oper = Op.ELEVADO
            # else: raise ValueError("---operador")

            operandos = texto.split(operador)

            parametros = [self.convertir_text(operandos[0]),self.convertir_text(operandos[1])]

            p1 = Param()
            p2 = Param()
            res = Param()
            
            if isinstance(parametros[0],float): p1.f = parametros[0]
            elif isinstance(parametros[0],list) and not isinstance(parametros[0][0],list): p1.v = parametros[0]
            elif isinstance(parametros[0],list) and isinstance(parametros[0][0],list): p1.m = parametros[0]
            # else: 

            if isinstance(parametros[1],float): p2.f = parametros[1]
            elif isinstance(parametros[1],list) and not isinstance(parametros[1][0],list): p2.v = parametros[1]
            elif isinstance(parametros[1],list) and isinstance(parametros[1][0],list): p2.m = parametros[1]
            # else:

            if operador == '+': res = self.client.suma(p1,p2)
            elif operador == '-': res = self.client.resta(p1,p2)
            elif operador == '*': res = self.client.multiplicacion(p1,p2,False)
            elif operador == '/': res = self.client.division(p1,p2)
            elif operador == 'x': res = self.client.multiplicacion(p1,p2,True)
            # else: 

            return res
        
        except ValueError: return None


    def get_message(self):
        try:
            return self.client.getWarnings()
        except ValueError: return "---****---"

root = tk.Tk()
app = App(root)
root.mainloop()