#!/bin/bash

# Init

#Задание 1:

mkdir -p lab0
cd lab0
touch carvanha4 flaaffy0 omanyte99
mkdir -p machoke7
cd machoke7
mkdir -p bronzong
touch omastar
touch marill
cd ..
mkdir -p tirtouga5
cd tirtouga5
touch beheeyem
touch pupitar
touch nidoking
cd ..
mkdir -p whirlpede9
cd whirlpede9
mkdir -p armaldo
touch slowpoke
mkdir -p tentacruel
mkdir -p minccino
cd ..

echo Ходы > carvanha4
echo "Ancientpower Bounce Dark Pulse Dive Fury Cutter Icy" >> carvanha4
echo "Wind Mud-Slap Sleep Talk Snore Spite Super Fang Swift Uproar Water" >> carvanha4
echo "Pulse Whirlpool Zen Headbutt" >> carvanha4
echo "weight=29.3 height=31.0 atk=6" > flaaffy0
echo "def=6" >> flaaffy0
cd machoke7
echo -n возможности > omastar
echo " Overland=5 Surface=9 Underwater=9 Jump2=0" >> omastar
echo "Power=2 Intelligence=4 Gilled=0" >> omastar
echo "satk=2 sdef=5" > marill
echo "spd=4" >> marill
cd ..
echo "satk=9 sdef=6 spd=4" > omanyte9
cd tirtouga5
echo "Развитые способности" > beheeyem
echo "Analytic" >> beheeyem
echo "satk=7 sdef=7 spd=5" > pupitar
echo "Развитые способности" > nidoking
echo "Hustle Sheer Force" >> nidoking
cd ..
cd whirlpede9
echo "Развитые способности Regenerator" > slowpoke

#Задание 2:
chmod 044 carvanha4
chmod 440 flaaffy0
cd machoke7
chmod 004 omastar
chmod 750 bronzong
chmod 604 marill
cd ..
chmod 357 machoke7
chmod 640 omanyte9
cd tirtouga5
chmod 004 beheeyem
chmod 440 pupitar
chmod 640 nidoking
cd ..
chmod 335 tirtouga5
cd whirlpede9
chmod 733 armaldo
chmod 004 slowpoke
chmod 577 tentacruel
chmod 573 minccino
cd ..
chmod 570 whirlpede9

#Задание 3:
chmod 777 tirtouga5
chmod 777 whirlpede9
chmod 777 whirlpede9/slowpoke
chmod 777 tirtouga5/beheeyem
chmod 777 omanyte9
chmod 777 flaaffy0
chmod 777 whirlpede9/minccino
chmod 777 whirlpede9/tentacruel
chmod 777 carvanha4
ln -s tirtouga5 Copy_70
cat whirlpede9/slowpoke tirtouga5/beheeyem > flaaffy0_53
ln -P omanyte9 tirtouga5/nidokingomanyte
cp flaaffy0 whirlpede9/minccino
cp -r whirlpede9/* whirlpede9/tentacruel
ln -s carvanha4 tirtouga5/pupitarcarvanha
cp omanyte9 tirtouga5/nidokingomanyte_omanyte_cp
chmod 004 whirlpede9/slowpoke
chmod 577 whirlpede9/tentacruel
chmod 573 whirlpede9/minccino
chmod 004 tirtouga5/beheeyem
chmod 570 whirlpede9
chmod 335 tirtouga5
chmod 440 flaaffy0
chmod 044 carvanha4
chmod 640 omanyte9

#Задание 4:
chmod 777 tirtouga5
chmod 777 whirlpede9/slowpoke
chmod 777 carvanha4
chmod 777 machoke7
chmod 777 tirtouga5/beheeyem
wc -l machoke7/omastar machoke7/marill | sort -nr
[ ! -z $(grep -rl "ke" .)] && ls -l $(grep -rl "ke" .) 2>&1
[ ! -z $(ls -1 -dp **/t* | grep -v "/$") ] && cat $(ls -1 -dp **/t* | grep -v "/$") | sort -r | nl 2> /tmp/opd_lab1_err>sort $(ls -1 -dp "$PWD/tirtouga5/"* | grep -v "/$") 2> /tmp/opd_lab1_errors4.log
cat -n $(ls -1 -dp "$PWD/whirlpede9/"* | grep -v "/$") 2> /dev/null
ls -ltr 2>&1 | grep 'g$' | tail -2
chmod 004 whirlpede9/slowpoke
chmod 004 tirtouga5/beheeyem
chmod 335 tirtouga5
chmod 044 carvanha4
chmod 357 machoke7

#Задание 5:
chmod 777 carvanha4
rm -f carvanha4
chmod 777 tirtouga5/nidoking
rm -f tirtouga5/nidoking
rm -f tirtouga5/pupitarcarvan*
rm -f tirtouga5/nidokingomany*
chmod 777 machoke7
rm -r machoke7
chmod -R 777 whirlpede9
rm -r whirlpede9/tentacruel