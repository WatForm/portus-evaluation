sig A {
  f: set A,
  g: set A
}

run test { some a: A | a.(f.g) = a }
