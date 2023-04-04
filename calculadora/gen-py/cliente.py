from calculadora import Calculadora
from calculadora.ttypes import Param, Trig
from decimal import Decimal, ROUND_HALF_UP
import sys
import numpy as np
import json
import re

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
                try:
                    if not isinstance(result,str):
                        if result != None:
                            if result.f==None and result.v==None and result.m==None: raise ValueError
                            else: self.result_label.config(text=json.dumps(r(result))) 
                        else: raise ValueError
                    else: raise TypeError
                except TypeError: self.result_label.config(text=result)
            except ValueError: self.result_label.config(text="---la operación no se ha realizado correctamente---")

            message = self.get_message()
            for i in range(len(message)):
                if "error" in message[i]: color = "red3"
                elif "warning" in message[i]: color = "orange2"
                else: color = "black"

                self.message_list.insert(tk.END, message[i])
                self.message_list.itemconfigure(self.message_list.size()-1, fg=color)
                
                #es para añadir los cambios, nada más


    def convertir_text(self,text):
        try:
            if str(text).startswith('[[') and str(text).endswith(']]'): return [ [ float(num) for num in fila.strip('[]').split(',') ] for fila in text.strip('[]').split('],[') ]
            elif str(text).startswith('[') and str(text).endswith(']'): return [ float(num) for num in text.strip('[]').split(',') ]
            else: return float(text)
        except ValueError: 
            print("La text no representa ningún tipo de dato válido (float, lista o matriz).")
            return None


    def calcular(self, text):
        try:
            texto = text.replace(" ","")

            un_param = False

            if '+' in texto: operador='+'
            elif '-' in texto: operador='-'
            elif '*' in texto: operador='*'
            elif '/' in texto: operador='/'
            elif 'x' in texto: operador='x'
            else:
                un_param = True
                if str(texto).startswith('sin(') : operador='sin'
                elif str(texto).startswith('cos('): operador='cos'
                elif str(texto).startswith('tan('): operador='tan'
                elif str(texto).startswith('arcsin('): operador='arcsin'
                elif str(texto).startswith('arccos('): operador='arccos'
                elif str(texto).startswith('arctan('): operador='arctan'
                elif str(texto).startswith('arcsinh('): operador='arcsinh'
                elif str(texto).startswith('arccosh('): operador='arccosh'
                else: return "---el operador no es válido---"

            if text.count(operador) > 1: raise ValueError

            operandos = []
            
            if not un_param: operandos = texto.split(operador)
            else: operandos.append(re.search(r"^{operador}\((.+)\)$".format(operador=re.escape(operador)),texto).group(1))

            p1 = Param()
            operando1 = self.convertir_text(operandos[0])

            if isinstance(operando1,float): p1.f = operando1
            elif isinstance(operando1,list) and not isinstance(operando1[0],list): p1.v = operando1
            elif isinstance(operando1,list) and isinstance(operando1[0],list): p1.m = operando1
            # else:
            
            if not un_param:
                p2 = Param()
                operando2 = self.convertir_text(operandos[1])
            
                if isinstance(operando2,float): p2.f = operando2
                elif isinstance(operando2,list) and not isinstance(operando2[0],list): p2.v = operando2
                elif isinstance(operando2,list) and isinstance(operando2[0],list): p2.m = operando2
                # else:

            res = Param()

            if not un_param:
                if operador == '+': res = self.client.suma(p1,p2)
                elif operador == '-': res = self.client.resta(p1,p2)
                elif operador == '*': res = self.client.multiplicacion(p1,p2,False)
                elif operador == '/': res = self.client.division(p1,p2)
                elif operador == 'x': res = self.client.multiplicacion(p1,p2,True)
            else:
                if operador == 'sin': res = self.client.trigonometria(p1,Trig.SIN)
                elif operador == 'cos': res = self.client.trigonometria(p1,Trig.COS)
                elif operador == 'tan': res = self.client.trigonometria(p1,Trig.TAN)
                elif operador == 'arcsin': res = self.client.trigonometria(p1,Trig.ARCSIN)
                elif operador == 'arccos': res = self.client.trigonometria(p1,Trig.ARCCOS)
                elif operador == 'arctan': res = self.client.trigonometria(p1,Trig.ARCTAN)
                elif operador == 'arcsinh': res = self.client.trigonometria(p1,Trig.ARCSINH)
                elif operador == 'arccosh': res = self.client.trigonometria(p1,Trig.ARCCOSH)

            return res
        
        except ValueError: return None


    def get_message(self):
        try:
            return self.client.getWarnings()
        except ValueError: return "---****---"

root = tk.Tk()
app = App(root)
root.mainloop()