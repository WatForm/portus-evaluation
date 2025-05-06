sig A { f: A }

run test_all { all x: A | x.f = x }
run test_some { some x: A | x.f = x }
run test_no { no x: A | x.f = x }
run test_one { one x: A | x.f = x }
run test_lone { lone x: A | x.f = x }
