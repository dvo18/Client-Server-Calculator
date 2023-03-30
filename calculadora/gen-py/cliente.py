from calculadora import Calculadora
from calculadora.ttypes import Param
from calculadora.ttypes import Tipo

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def r(f):
    res = round(f,3)
    return str(res).rstrip('0').rstrip('.')

transport = TSocket.TSocket("localhost", 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = Calculadora.Client(protocol)

transport.open()

print("hacemos ping al server")
client.ping()

p1 = Param(t=1,p=Tipo(f=1))
p2 = Param(t=2,p=Tipo(v=[2,3,4]))

resultado = client.suma(p1, p2)
for f in resultado.p.v:
    print(r(f))

transport.close()
