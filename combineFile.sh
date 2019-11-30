root=`pwd`
fitsPath=~/haha/
sourceName=haha
sourceRA=05:31:58.7
sourceDEC=+33:08:52.5

cd ${root}/
cd ${fitsPath}
ls *.fits > fitslist.txt
./combine_fits ${root}/${sourceName} fitslist.txt 
./update_Header-OFFSSUB ${sourceName}.fits
