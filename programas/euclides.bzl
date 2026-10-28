Main |:
    <w> "Escribe dos numeros"
    <?> x
    <?> y
    Mcd x y
:|

Mcd a b |:
    if b = 0 |:
        <w> "Su MCD es" a
    :| else |:
        Mcd b (a % b)
    :|
:|