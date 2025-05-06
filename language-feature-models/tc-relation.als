sig A {
  f: set A
}

run test { some a: A | a.^f = a }
