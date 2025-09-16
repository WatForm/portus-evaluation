"""
	This script removes expert models that use features Portus doesn't/won't support.
	This is done in Python rather than bash to support Windows and Linux pathnames.
"""

import os
from pathlib import Path 

rmfiles = []

# Uses an expression of the form (*f).(*g), which we don't support because we need to merge the middle column's
# sorts together so that we can quantify over the middle column, but (*f).(*g)'s middle column includes both Int
# and other sorts, and we can't merge Int with other sorts because it's a builtin.
rmfiles.append(Path("expert-models/5x4l2fj5nfbq3cz2dumwdt57g3kig3rd-litmustestgen/power_perturbed.als"))

# Uses unsupported forms of higher-order quantification.
rmfiles.append(Path("expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/parallel.als"))
rmfiles.append(Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/synchronsation/sync.als"))
rmfiles.append(Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/firewire/firewire.als"))
rmfiles.append(Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/models/transport/railway.als"))
rmfiles.append(Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/puzzles/8-queens/queens.als"))

# This model uses a form of higher-order quantification supported by Portus but not by Kodkod. We also exclude it
# from performance testing.
rmfiles.append(Path("expert-models/gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/algorithms/discovery/ins.als"))

# Uses a field bounded by "univ", which is not supported.
rmfiles.append(Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/nwk/discovery.als"))
rmfiles.append(Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/associate.als"))
rmfiles.append(Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_direct.als"))
rmfiles.append(Path("expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/test/join_orphan.als"))

for f in rmfiles:
	os.remove(f)
