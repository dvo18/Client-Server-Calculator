
union Param {
    1: double f,
    2: list<double> v,
    3: list<list<double>> m
}

service Calculadora{
   void ping(),
   Param suma(1:Param p1, 2:Param p2),
}
