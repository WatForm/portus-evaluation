open util/ordering[A]
sig A {}

run { all a: A | a.next != first }
run { all a: A | lte[first, a] }
run { all a: A | gte[a, first] }
