import glob
import sys
import numpy as np

from calculadora import Calculadora
from calculadora.ttypes import Param, Trig

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import logging

logging.basicConfig(level=logging.DEBUG)

# comprobar que los tamaños de una fila son los mismos
def c(m):
    return all(len(row) == len(m[0]) for row in m)

class CalculadoraHandler:
    def __init__(self):
        self.log = {}
        self.msg_warning = ""
        self.warnings = [
            "\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el número de columnas de la primera matriz debe ser igual al número de filas de la segunda---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el formato de los parámetros no es correcto---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: no se puede dividir por cero (contiene el cero)---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el tamaño de las matrices debe ser el mismo---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: los vectores no tienen igual tamaño---\033[0m",
            "\033[33m---\033[1;33mwarning\033[0;33m: se está calculando el producto escalar---\033[0m",
            "\033[33m---\033[1;33mwarning\033[0;33m: matemáticamente el producto vectorial se realiza sobre vectores de dimension 3---\033[0m",
            "\033[33m---\033[1;33mwarning\033[0;33m: el producto vectorial de dos vectores de tamaño 2 darán como resultado un entero---\033[0m",
            "\033[33m---\033[1;33mwarning\033[0;33m: se está calculando el producto vectorial---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el producto vectorial se debe aplicar sobre vectores de tamaño igual o menor que 3---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el producto vectorial se debe aplicar sobre vectores de tamaño mayor a 1---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el valor debe estar entre -1 y 1---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: la función trigonométrica no existe o no se ha implementado aún---\033[0m",
            "\033[31m---\033[1;31merror\033[0;31m: el formato del parámetro no es correcto---\033[0m"
        ]

    def ping(self):
        self.msg_warning = ""
        return "ping() recibido"
    
    def setWarnings(self,tipo):
        if tipo>=0 and tipo<=len(self.warnings):
            for i in range(len(self.warnings)):
                self.msg_warning += self.warnings[i] + "\n"

    def getWarnings(self):
        return self.msg_warning

    def suma(self, p1, p2):
        try:
            r = Param()

            try:
                if p1.f !=None:
                    if p2.f !=None: r.f = p1.f+p2.f
                    elif p2.v !=None: r.v = np.add(p1.f,np.array(p2.v))
                    elif p2.m !=None:
                        try:
                            if c(p2.m): r.m = np.add(p1.f,np.array(p2.m))
                            else: raise TypeError
                        except TypeError: self.setWarnings(0)
                    else: raise ValueError

                elif p1.v !=None:
                    if p2.f !=None: r.v = np.add(np.array(p1.v),p2.f)
                    elif p2.v !=None:
                        try:
                            if len(p1.v)==len(p2.v): r.v = np.add(np.array(p1.v),np.array(p2.v))
                            else: raise ValueError
                        except ValueError as e1: self.setWarnings(6)
                    elif p2.m !=None:
                        try:
                            try:
                                if c(p2.m):
                                    if len(p1.v)==len(p2.m): r.m = [ [ p1.v[i]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                                    elif len(p1.v)==len(p2.m[0]): r.m = np.add(np.array(p1.v),np.array(p2.m))
                                    else: raise ValueError
                                else: raise TypeError
                            except ValueError as e2: self.setWarnings(1)
                        except TypeError: self.setWarnings(0)
                    else: raise ValueError

                elif p1.m !=None:
                    try:
                        if c(p1.m):
                            if p2.f !=None: r.m = np.add(np.array(p1.m),p2.f)
                            elif p2.v !=None:
                                try:
                                    if len(p1.m)==len(p2.v): r.m = [ [ p1.m[i][j]+p2.v[i] for j in range(len(p1.m[i])) ] for i in range(len(p1.m)) ]
                                    elif len(p1.m[0])==len(p2.v): r.m = np.add(np.array(p1.m),np.array(p2.v))
                                    else: raise ValueError
                                except ValueError as e3: self.setWarnings(1)
                            elif p2.m !=None:
                                try:
                                    if c(p2.m):
                                        if len(p1.m)==len(p2.m) and len(p1.m[0])==len(p2.m[0]): r.m = np.add(np.array(p1.m),np.array(p2.m))
                                        else: raise ValueError
                                    else: raise TypeError
                                except ValueError as e4: self.setWarnings(5)
                            else: raise ValueError
                        else: raise TypeError
                    except TypeError: self.setWarnings(0)
                
                else: raise ValueError

            except ValueError as eG: self.setWarnings(3)
            
            return r
        
        except Exception as e:
            print(e)
            raise e
        

    def resta(self, p1, p2):
        try:
            if p2.f !=None: p2.f = -p2.f
            elif p2.v !=None: p2.v = [ -x for x in p2.v ]
            elif p2.m !=None: p2.m = [ [ -c for c in f ] for f in p2.m ]
            else: raise TypeError
            
            return self.suma(p1,p2)
        except TypeError: self.setWarnings(3)


    def multiplicacion(self, p1, p2, prodVec):
        try:
            r = Param()

            try:
                if p1.f !=None:
                    if p2.f !=None: r.f = p1.f*p2.f
                    elif p2.v !=None: r.v = np.dot(p1.f,np.array(p2.v))
                    elif p2.m !=None:
                        try:
                            if c(p2.m): r.m = np.dot(p1.f,np.array(p2.m))
                            else: raise TypeError
                        except TypeError: self.setWarnings(0)
                    else: raise ValueError

                elif p1.v !=None:
                    if p2.f !=None: r.v = np.dot(np.array(p1.v),p2.f)
                    elif p2.v !=None:
                        if not prodVec:
                            try:
                                if len(p1.v)==len(p2.v):
                                    self.setWarnings(7)
                                    r.f = np.dot(np.array(p1.v),np.array(p2.v))
                                else: raise ValueError
                            except ValueError as e1_1: self.setWarnings(6)
                        else:
                            try:
                                if len(p1.v)!=1 and len(p2.v)!=1:
                                    try:
                                        if len(p1.v)<=3 and len(p2.v)<=3:
                                            if len(p1.v)==2 and len(p2.v)==2:
                                                self.setWarnings(8)
                                                self.setWarnings(9)
                                                r.f = np.cross(np.array(p1.v),np.array(p2.v))
                                            else:
                                                self.setWarnings(10)
                                                if len(p1.v)==2 or len(p2.v)==2: self.setWarnings(8)
                                                r.v = np.cross(np.array(p1.v),np.array(p2.v))
                                        else: raise ValueError
                                    except ValueError as e1_2: self.setWarnings(11)
                                else: raise ValueError
                            except ValueError as e1_3: self.setWarnings(12)
                    elif p2.m !=None:
                        try:
                            try:
                                if c(p2.m):
                                    if len(p1.v)==len(p2.m): r.v = np.dot(np.array(p1.v),np.array(p2.m)).tolist()
                                    elif len(p1.v)==len(p2.m[0]): r.v = np.dot(np.array(p2.m),np.array(p1.v))
                                    else: raise ValueError
                                else: raise TypeError
                            except ValueError as e2: self.setWarnings(1)
                        except TypeError: self.setWarnings(0)
                    else: raise ValueError

                elif p1.m !=None:
                    try:
                        if c(p1.m):
                            if p2.f !=None: r.m = np.dot(p2.f,np.array(p1.m))
                            elif p2.v !=None:
                                try:
                                    if len(p1.m)==len(p2.v): r.v = np.dot(np.array(p2.v),np.array(p1.m))
                                    elif len(p1.m[0])==len(p2.v): r.v = np.dot(np.array(p1.m),np.array(p2.v))
                                    else: raise ValueError
                                except ValueError as e3: self.setWarnings(1)
                            elif p2.m !=None:
                                try:
                                    if c(p2.m):
                                        if len(p1.m[0])==len(p2.m): r.m = np.dot(np.array(p1.m),np.array(p2.m))
                                        else: raise ValueError
                                    else: raise TypeError
                                except ValueError as e4: self.setWarnings(2)
                            else: raise ValueError
                        else: raise TypeError
                    except TypeError: self.setWarnings(0)
        
                else: raise ValueError

            except ValueError as eG: self.setWarnings(3)
            
            return r
        
        except Exception as e:
            print(e)
            raise e


    def division(self, p1, p2):
        try:
            try:
                if p2.f !=None:
                    if p2.f!=0: p2.f = 1/p2.f
                    else: raise ZeroDivisionError
                elif p2.v !=None:
                    if not 0 in p2.v: p2.v = [ -x/len(p2.v)**2 for x in p2.v ]        # inverso multiplicativo
                    else: raise ZeroDivisionError
                elif p2.m !=None: 
                    if not any(0 in f for f in p2.m): p2.m = np.linalg.inv(np.array(p2.m)).tolist()
                    else: raise ZeroDivisionError
                else: raise TypeError

                return self.multiplicacion(p1,p2,False)
            except ZeroDivisionError: self.setWarnings(4)
        except TypeError: self.setWarnings(3)

    def trigonometria(self, p, t):
        
        newp = Param()
        n = None
        r = None

        try:
            if p.f !=None: n=p.f
            elif p.v !=None: n=np.array(p.v)
            elif p.m !=None: n=np.array(p.m)
            else: raise TypeError

            try:
                if t is Trig.SIN: r=np.sin(n)
                elif t is Trig.COS: r=np.cos(n)
                elif t is Trig.TAN: r=np.tan(n)

                elif t is Trig.ARCCOS: 
                    if (p.f!=None and n>=-1 and n<=1) or (p.v!=None and np.all((-1<=n)&(n<=1))) or (p.m!=None and np.all((-1<=n)&(n<=1))):
                        r=np.arcsin(n)
                    else: self.setWarnings(13)
                elif t is Trig.ARCSIN:
                    if (p.f!=None and n>=-1 and n<=1) or (p.v!=None and np.all((-1<=n)&(n<=1))) or (p.m!=None and np.all((-1<=n)&(n<=1))):
                        r=np.arccos(n)
                    else: self.setWarnings(13)
                elif t is Trig.ARCTAN:
                    if (p.f!=None and n>=-1 and n<=1) or (p.v!=None and np.all((-1<=n)&(n<=1))) or (p.m!=None and np.all((-1<=n)&(n<=1))):
                        r=np.arctan(n)
                    else: self.setWarnings(13)
                
                elif t is Trig.ARCSINH: r=np.arcsinh(n)
                elif t is Trig.ARCCOSH: r=np.arccosh(n)
                else:  raise TypeError

            except TypeError as t1: self.setWarnings(14)  
        
            if p.f !=None: newp.f=r
            elif p.v !=None: newp.v=r
            elif p.m !=None: newp.m=r
            else: TypeError
            
        except TypeError as t2: self.setWarnings(15)

        return newp


if __name__ == "__main__":
    handler = CalculadoraHandler()
    processor = Calculadora.Processor(handler)
    transport = TSocket.TServerSocket(host="127.0.0.1", port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print("iniciando servidor...")
    server.serve()
    print("fin")
