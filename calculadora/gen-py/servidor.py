import glob
import sys

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
                    elif p2.v !=None: r.v = [ p1.f+x for x in p2.v]                     # comprensión de listas
                    elif p2.m !=None: r.m = [ [ c+p1.f for c in f ] for f in p2.m ]     # comprensión de listas
                    else: raise ValueError

                elif p1.v !=None:
                    if p2.f !=None: r.v = [ x+p2.f for x in p1.v ]
                    elif p2.v !=None:
                        try:
                            if len(p1.v)==len(p2.v): r.v = [ p1.v[i]+p2.v[i] for i in range(len(p1.v)) ]
                            else: raise ValueError
                        except ValueError as e1: print("---los vectores no tienen igual tamaño---")
                    elif p2.m !=None:
                        try:
                            if len(p1.v)==len(p2.m): r.m = [ [ p1.v[i]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                            elif len(p1.v)==len(p2.m[0]): r.m = [ [ p1.v[j]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                            else: raise ValueError
                        except ValueError as e2: print("---el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---")
                    else: raise ValueError

                elif p1.m !=None:
                    try:
                        if c(p1.m):
                            if p2.f !=None: r.m = [ [ c+p2.f for c in f ] for f in p1.m ]
                            elif p2.v !=None:
                                try:
                                    if len(p1.m)==len(p2.v): r.m = [ [ p1.m[i][j]+p2.v[i] for j in range(len(p1.m[i])) ] for i in range(len(p1.m)) ]
                                    elif len(p1.m[0])==len(p2.v): r.m = [ [ p1.m[i][j]+p2.v[j] for j in range(len(p1.m[i])) ] for i in range(len(p1.m)) ]
                                    else: raise ValueError
                                except ValueError as e3: print("---el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---")
                            elif p2.m !=None:
                                try:
                                    if c(p2.m):
                                        if len(p1.m)==len(p2.m) and c(p2.m) and p1.m[0]==p2.m[0]: r.m = [ [ p1.m[i][j]+p2.m[i][j] for j in range(len(p1.m[0])) ] for i in range(len(p1.m)) ]
                                        else: raise ValueError
                                    else: raise TypeError
                                except ValueError as e4: print("---el tamaño de las matrices debe ser el mismo---")
                            else: raise ValueError
                        else: raise TypeError
                    except TypeError: print("---el tamaño de todas las filas de las matrices debe ser el mismo---")

                else: raise ValueError

            except ValueError as eG: print("---el formato de los parámetros no es correcto---")
            
            return r
        
        except Exception as e:
            print(e)
            raise e
        

    def resta(self, p1, p2):
        try:
            if p2.f !=None: p2.f = -p2.f
            elif p2.v !=None: p2.v = [ -x for x in p2.v ]
            elif p2.m !=None: [ [ -c for c in f ] for f in p2.m ]
            else: raise TypeError

            self.suma(p1,p2)
        except TypeError: print("---el formato de los parámetros no es correcto---")



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
