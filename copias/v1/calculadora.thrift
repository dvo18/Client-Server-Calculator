
union Tipo {
    1: double f,
    2: list<double> v,
    3: list<list<double>> m
}

struct Param {
    1: i32 t,
    2: Tipo p
}

service Calculadora{
   void ping(),
   Param suma(1:Param p1, 2:Param p2),
}
