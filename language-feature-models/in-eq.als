sig B {}
one sig A { f, g: set B }

run test_in { A.f in A.g }
run test_eq { A.f = A.g }
