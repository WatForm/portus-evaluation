"""
	This bash scripts removes expert models that use features Portus doesn't/won't support
	This is done in python rather than bash to support Windows and Linux pathnames
"""

import os
from pathlib import Path 

rmfiles = []

# ?? why is this one removed?  something about (*f).(*g) ??
expert-models/5x4l2fj5nfbq3cz2dumwdt57g3kig3rd-litmustestgen/power_perturbed.als

# Meta
rmfiles.append( Path("expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/hc-atd/hc7.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/einstein/einstein-wikipedia.als"))

# Quantifying over (n>1)-tuples
rmfiles.append( Path("expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/parallel.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/synchronsation/sync.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/coloring/color-australia.als"))

# Quantifying over sets (e.g. "all x: set | ...")
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/discovery/ins.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/logic/syllogism/syllogism.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/firewire/firewire.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/transport/railway.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/simple-models/state-machine/flip-flop.als"))
# Note: these do it for some checks, but we can just remove them
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/simple-models/books/birthday.als"))

# Strings
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs.als"))
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs_inst.als"))
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs.als"))
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/FM2CF/fm2cfs.als"))
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/HSM2NHSM/NHSM.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/ietf-rfcs/rfc7617-BasicAuth/basic-auth.als"))
rmfiles.append( Path("expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs_inst.als"))

# Quantification over univ
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/logic/philosophers.als"))
# NAD: these aren't needed for expert-models
#rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/associate_indication.als
#rm expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/join_orphan.als
rmfiles.append( Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/discovery.als"))
rmfiles.append( Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/associate.als"))
rmfiles.append( Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_direct.als"))
rmfiles.append( Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_orphan.als"))

# Using integer join in unsupported ways (should be improved?), e.g. "q.univ" where q: Int->Int
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/8-queens/queens.als"))
rmfiles.append( Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/money.als"))

# Too-clever uses of int
# Chord uses integer/min, which makes a singular int like "S - S.next", which
# is too clever for us
rmfiles.append( Path("expert-models/chord-pamela-zave/correctChord.als"))

for f in rmfiles:
	os.remove(f)