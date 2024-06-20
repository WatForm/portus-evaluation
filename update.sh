git pull
cd ..
cd org.alloytools.alloy
git checkout portus
git submodule init
git submodule update --recursive --remote
jenv local 13
./gradlew clean
./gradlew build
cd ../portus-evaluation