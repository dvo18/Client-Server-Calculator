
union Param {
    1: double f,
    2: list<double> v,
    3: list<list<double>> m
}

enum Trig {
    SIN=1,
    COS=2,
    TAN=3,
    ARCSIN=4,
    ARCCOS=5,
    ARCTAN=6,
    ARCSINH=7,
    ARCCOSH=8,
    ARCTANH=9
}

service Calculadora{
   string ping(),
   Param suma(1:Param p1, 2:Param p2),
   Param resta(1:Param p1, 2:Param p2),
   Param multiplicacion(1:Param p1, 2:Param p2, 3:bool prodVec),
   Param division(1:Param p1, 2:Param p2),
   Param trigonometria(1:Param p1, 2:Trig func),
   list<string> getWarnings(),
}
