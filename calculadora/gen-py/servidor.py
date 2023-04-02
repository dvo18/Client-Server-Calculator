import glob
import sys
import numpy as np

from calculadora import Calculadora
from calculadora.ttypes import Param

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

    def ping(self):
        print("me han hecho ping()")


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
                        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")
                    else: raise ValueError

                elif p1.v !=None:
                    if p2.f !=None: r.v = np.add(np.array(p1.v),p2.f)
                    elif p2.v !=None:
                        try:
                            if len(p1.v)==len(p2.v): r.v = np.add(np.array(p1.v),np.array(p2.v))
                            else: raise ValueError
                        except ValueError as e1: print("\033[31m---\033[1;31merror\033[0;31m: los vectores no tienen igual tamaño---\033[0m")
                    elif p2.m !=None:
                        try:
                            try:
                                if c(p2.m):
                                    if len(p1.v)==len(p2.m): r.m = [ [ p1.v[i]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                                    elif len(p1.v)==len(p2.m[0]): r.m = np.add(np.array(p1.v),np.array(p2.m))
                                    else: raise ValueError
                                else: raise TypeError
                            except ValueError as e2: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---\033[0m")
                        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")
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
                                except ValueError as e3: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---\033[0m")
                            elif p2.m !=None:
                                try:
                                    if c(p2.m):
                                        if len(p1.m)==len(p2.m) and len(p1.m[0])==len(p2.m[0]): r.m = np.add(np.array(p1.m),np.array(p2.m))
                                        else: raise ValueError
                                    else: raise TypeError
                                except ValueError as e4: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de las matrices debe ser el mismo---\033[0m")
                            else: raise ValueError
                        else: raise TypeError
                    except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")

                else: raise ValueError

            except ValueError as eG: print("\033[31m---\033[1;31merror\033[0;31m: el formato de los parámetros no es correcto---\033[0m")
            
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
        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el formato de los parámetros no es correcto---\033[0m")


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
                        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")
                    else: raise ValueError

                elif p1.v !=None:
                    if p2.f !=None: r.v = np.dot(np.array(p1.v),p2.f)
                    elif p2.v !=None:
                        if not prodVec:
                            try:
                                if len(p1.v)==len(p2.v):
                                    print("\033[33m---\033[1;33mwarning\033[0;33m: se está calculando el producto escalar---\033[0m")
                                    r.f = np.dot(np.array(p1.v),np.array(p2.v))
                                else: raise ValueError
                            except ValueError as e1_1: print("\033[31m---\033[1;31merror\033[0;31m: los vectores no tienen igual tamaño---\033[0m")
                        else:
                            try:
                                if len(p1.v)!=1 and len(p2.v)!=1:
                                    try:
                                        if len(p1.v)<=3 and len(p2.v)<=3:
                                            if len(p1.v)==2 and len(p2.v)==2:
                                                print("\033[33m---\033[1;33mwarning\033[0;33m: matemáticamente el producto vectorial se realiza sobre vectores de dimension 3---\033[0m")
                                                print("\033[33m---\033[1;33mwarning\033[0;33m: el producto vectorial de dos vectores de tamaño 2 darán como resultado un entero---\033[0m")
                                                r.f = np.cross(np.array(p1.v),np.array(p2.v))
                                            else:
                                                print("\033[33m---\033[1;33mwarning\033[0;33m: se está calculando el producto vectorial---\033[0m")
                                                if len(p1.v)==2 or len(p2.v)==2: print("\033[33m---\033[1;33mwarning\033[0;33m: matemáticamente el producto vectorial se realiza sobre vectores de dimension 3---\033[0m")
                                                r.v = np.cross(np.array(p1.v),np.array(p2.v))
                                        else: raise ValueError
                                    except ValueError as e1_2: print("\033[31m---\033[1;31merror\033[0;31m: el producto vectorial se debe aplicar sobre vectores de tamaño igual o menor que 3---\033[0m")
                                else: raise ValueError
                            except ValueError as e1_3: print("\033[31m---\033[1;31merror\033[0;31m: el producto vectorial se debe aplicar sobre vectores de tamaño mayor a 1---\033[0m")
                    elif p2.m !=None:
                        try:
                            try:
                                if c(p2.m):
                                    if len(p1.v)==len(p2.m): r.v = np.dot(np.array(p1.v),np.array(p2.m)).tolist()
                                    elif len(p1.v)==len(p2.m[0]): r.v = np.dot(np.array(p2.m),np.array(p1.v))
                                    else: raise ValueError
                                else: raise TypeError
                            except ValueError as e2: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---\033[0m")
                        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")
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
                                except ValueError as e3: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---\033[0m")
                            elif p2.m !=None:
                                try:
                                    if c(p2.m):
                                        if len(p1.m[0])==len(p2.m): r.m = np.dot(np.array(p1.m),np.array(p2.m))
                                        else: raise ValueError
                                    else: raise TypeError
                                except ValueError as e4: print("\033[31m---\033[1;31merror\033[0;31m: el número de columnas de la primera matriz debe ser igual al número de filas de la segunda---\033[0m")
                            else: raise ValueError
                        else: raise TypeError
                    except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el tamaño de todas las filas de las matrices debe ser el mismo---\033[0m")

                else: raise ValueError

            except ValueError as eG: print("\033[31m---\033[1;31merror\033[0;31m: el formato de los parámetros no es correcto---\033[0m")
            
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
                    if not 0 in p2.v: p2.v = [ 1/x for x in p2.v ]
                    else: raise ZeroDivisionError
                elif p2.m !=None: 
                    if not any(0 in f for f in p2.m): p2.m = [ [ 1/c for c in f ] for f in p2.m ]
                    else: raise ZeroDivisionError
                else: raise TypeError

                return self.multiplicacion(p1,p2,True)
            except ZeroDivisionError: print("\033[31m---\033[1;31merror\033[0;31m: no se puede dividir por cero (contiene el cero)---\033[0m")
        except TypeError: print("\033[31m---\033[1;31merror\033[0;31m: el formato de los parámetros no es correcto---\033[0m")



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
