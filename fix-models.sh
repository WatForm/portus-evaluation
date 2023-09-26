# This script fixes up the models downloaded by get-expert-models.sh by converting
# to Alloy 6 and performing other model-specific changes.
# Assumes the working directory is where get-expert-models.sh has cloned all the
# models to.

# === Alloy 6 syntax changes ===
# Replace ' with " throughout all files and append " after all Alloy 6 keywords.
# See http://alloytools.org/alloy6.html
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak "s/'/\"/g"
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/after/after\"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/always/always"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/before/before"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/enabled/enabled"/g'
# Don't replace 'event' because it isn't used in a conflicting way,
# but is used for some module names.
#find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/event/event"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/eventually/eventually"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/historically/historically"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/invariant/invariant"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/modifies/modifies"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/once/once"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/releases/releases"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/since/since"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/steps/steps"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/triggered/triggered"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/until/until"/g'
find . -type f -name "*.als" -print0 | xargs -0 sed -i.bak 's/var/var"/g'

# === Changes for specific models ===

# dbs_inst.als: lowercase "DBS" -> "dbs" in a module open declaration to match the
# case of the corresponding dbs.als file.
sed -i.bak 's/open DBS/open dbs/g' 7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs_inst.als
sed -i.bak 's/open DBS/open dbs/g' 7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs_inst.als

# trace.als: change predtotalOrder to pred/totalOrder
sed -i.bak "s/predtotalOrder/pred\/totalOrder/g" 7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/ElevatorSPL/trace.als
sed -i.bak "s/predtotalOrder/pred\/totalOrder/g" gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/utilities/trace/trace.als

# event.als: change LongEventspans to LongEvent.spans (typo?)
# Update: not actually necessary; not present in the downloaded model
#sed -i.bak 's/LongEventspans/LongEvent\.spans/g' lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/base/event.als

# birthday.als: the AddWorks and BusyDay assertions use constructs Portus doesn't support,
# but we support all the rest of the assertions.
# Comment out the specific lines.
sed -i.bak -e '50,53s/^/\/\//' -e '61s/^/\/\//' -e '64,68s/^/\/\//' gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models/simple-models/books/birthday.als

# Get rid of the .bak files caused by the portable sed syntax
# (see https://unix.stackexchange.com/a/92907)
find . -type f -name "*.als.bak" -print0 | xargs -0 rm
