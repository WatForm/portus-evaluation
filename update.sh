git pull
cd ..
cd org.alloytools.alloy
git pull
git checkout portus
git submodule init
git submodule update --recursive --remote
jenv local 12
./gradlew clean
./gradlew build
cd ../portus-evaluation
