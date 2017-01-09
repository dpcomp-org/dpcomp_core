echo 'Setup dawa'
cd ./dawa
./setup.sh
cd ..

echo 'Setup ahp'
cd ./ahp
./setup.sh
cd ..


echo 'Setup Thirdparty packages'
cd ./thirdparty

echo ' -- Acs12'
cd Acs12
./setup.sh
cd ..

echo ' -- xiaokui'
cd xiaokui
./setup.sh
cd ..

cd ..
