sig A {
  f: A -> A -> one B
}
sig B {}
run range1 {} for 4 A, 4 B
run range2 {} for 8 A, 8 B
run range3 {} for 16 A, 16 B
run range4 {} for 32 A, 32 B
