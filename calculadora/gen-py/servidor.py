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


class CalculadoraHandler:
    def __init__(self):
        self.log = {}

    def ping(self):
        print("me han hecho ping()")

    def suma(self, p1, p2):
        try:
            r = Param()

            if p1.f !=None:
                if p2.f !=None: r.f = p1.f+p2.f
                elif p2.v !=None: r.v = [ p1.f+x for x in p2.v]         # comprensión de listas
                else: r.m = [ [ c+p1.f for c in f ] for f in p2.m ]     # comprensión de listas

            elif p1.v !=None:
                if p2.f !=None: r.v = [ x+p2.f for x in p1.v ]
                elif p2.v !=None:
                    try:
                        if len(p1.v)==len(p2.v): r.v = [ p1.v[i]+p2.v[i] for i in range(len(p1.v)) ]
                        else: raise ValueError
                    except ValueError: print("---los vectores no tienen igual tamaño---")
                else:
                    try:
                        if len(p1.v)==len(p2.m): r.m = [ [ p1.v[i]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                        elif len(p1.v)==len(p2.m[0]): r.m = [ [ p1.v[j]+p2.m[i][j] for j in range(len(p2.m[i])) ] for i in range(len(p2.m)) ]
                        else: raise ValueError
                    except ValueError: print("---el tamaño del vector debe ser el mismo que el número de filas o columnas de la matriz---")
            
            return r
        
        except Exception as e:
            print(e)
            raise e


        # print("sumando " + str(p1) + " con " + str(n2))
        # return n1 + n2

    # def resta(self, n1, n2):
        # print("restando " + str(n1) + " con " + str(n2))
        # return n1 - n2


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
