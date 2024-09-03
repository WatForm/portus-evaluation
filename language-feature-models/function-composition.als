sig A {
  f: A,
  g: A
}

run test { some a: A | a.(f.g) = a } for 4 A
