sig A {
  f: one A
}
run test { some a: A | a.^f = a }
