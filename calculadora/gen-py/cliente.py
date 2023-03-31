from calculadora import Calculadora
from calculadora.ttypes import Param
from decimal import Decimal, ROUND_HALF_UP
import sys

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

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

p1 = Param(f=1)
p2 = Param(f=1)        # no hay error si alguna de las filas es menor arreglar

try:
    resultado = client.res
    if resultado.f==None and resultado.v==None and resultado.m==None: raise ValueError
except ValueError:
    print("---la operación no se ha realizado correctamente---")
    sys.exit
else:
    print(r(resultado))

transport.close()
