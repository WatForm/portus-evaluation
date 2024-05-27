# These commands were created from running catalyst to find all Alloy models on the list
# and then going through the log.txt file to extract the git clone commands for the ones 
# that Elias used as his expert models, which are listed in the README at:
# https://github.com/WatForm/static-profiling-of-alloy-models

download () {
  # Syntax: download <repo> <commit> <directory>
  # This downloads only the particular commit and not the whole repo.
  # See https://stackoverflow.com/a/3489576
  mkdir -p "$3"
  cd "$3"
  git init
  git remote add origin "$1"
  git fetch origin "$2"
  git reset --hard FETCH_HEAD
  cd ..
}

mkdir expert-models
cd expert-models
download https://github.com/ogiroux/talks.git a837092e73024383ab0e5bbace3f6b18ffbc655d 2scxlb3tbo5bmvmwplglqils7a5uarmx-talks
download https://github.com/atdyer/alloy.git 09cbc14fc85bfea4f95351e4c921d091ecc8b94d 3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy
download https://github.com/pron/amazon-snapshot-spec.git 9c60cb18151889d7b4c0a4ffd7de0b6fc2db0fb2 7d25ioxqmue65lp6ntzz735gpbg4fmgq-amazon-snapshot-spec
download https://github.com/nmacedo/MSV.git 6170c1473407d75ab2949ef6dcbb243b210d009c 7z32luflamhdcixvt6nwznnud4oi6dbr-MSV
download https://github.com/BGCX261/zigbee-alloy-svn-to-git.git 020bdb6a648a547e6bf1476533b602c4badaf82a lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git
download https://github.com/hkhojasteh/CANBus.git f6c7b8966de590cbb61176a919dbe49c02e733b0 oujlbmnutprdhddstyudppn7t35n43os-CANBus
download https://github.com/NVlabs/litmustestgen.git 580bd7434b7ca9206f0eccbdcffe6d212eeb0994 5x4l2fj5nfbq3cz2dumwdt57g3kig3rd-litmustestgen
download https://github.com/AlloyTools/models.git b9378ecf56a49ec65530a19214955e5203c26e08 gumxtrzzbkrtwi7jtwyu7eibi3fwhgmf-models
download https://github.com/nadeshr/weak_atomics.git 61ee841c8710cd6d2bea2041b49291a61f840b35 x7tjf3r7wnejcplj75s2o6im45kjodhs-weak_atomics
download https://github.com/naorinh/TransForm.git ff5c052adbc8ad0b11f9652f4886925216242516 x7t75qqe5fr6uzitot5sdu63o7drnur5-TransForm

mkdir chord-pamela-zave
cd chord-pamela-zave
wget https://www.pamelazave.com/correctChord.als
