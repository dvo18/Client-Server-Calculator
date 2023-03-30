import glob
import sys

from calculadora import Calculadora
from calculadora.ttypes import Tipo
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

            if p1.t==1:
                if p2.t==1: r.t=1; r.p=Tipo(f=p1.p.f+p2.p.f)

                elif p2.t==2:
                    r.t=2; r.p=Tipo(v=[])
                    for f in p2.p.v: r.p.v.append(f+p1.p.f)
            
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
