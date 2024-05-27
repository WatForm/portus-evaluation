# This bash scripts removes expert models that use features Portus doesn't/won't support

# Meta
rm expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/hc-atd/hc7.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/einstein/einstein-wikipedia.als

# Quantifying over (n>1)-tuples
rm expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/parallel.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/synchronisation/sync.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/coloring/color-australia.als

# Quantifying over sets (e.g. "all x: set | ...")
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/discovery/ins.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/logic/syllogism/syllogism.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/firewire/firewire.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/transport/railway.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/simple-models/state-machine/flip-flop.als
# Note: these do it for some checks, but we can just remove them
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/simple-models/books/birthday.als

# Strings
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs.als
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs_inst.als
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs.als
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/FM2CF/fm2cfs.als
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/HSM2NHSM/NHSM.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/ietf-rfcs/rfc7617-BasicAuth/basic-auth.als
rm expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs_inst.als

# Quantification over univ
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/logic/philosophers.als
# NAD: these aren't needed for expert-models
#rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/associate_indication.als
#rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/join_orphan.als
rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/discovery.als
rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/associate.als
rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_direct.als
rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_orphan.als

# Using integer join in unsupported ways (should be improved?), e.g. "q.univ" where q: Int->Int
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/8-queens/queens.als
rm expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/money.als

# Too-clever uses of int
# Chord uses integer/min, which makes a singular int like "S - S.next", which
# is too clever for us
rm expert-models/chord-pamela-zave/correctChord.als