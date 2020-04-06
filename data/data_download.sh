wget http://dap.ceda.ac.uk/thredds/fileServer/badc/cru/data/cru_ts/cru_ts_4.03/data/pre/cru_ts4.03.1901.2018.pre.dat.nc.gz
wget https://climexp.knmi.nl/data/iersst_nino3.4a_rel.dat
wget https://climexp.knmi.nl/data/ipdo.dat

yr=1880
while [ $yr -le 2020 ]; do
nm=1
while [ $nm -le 12 ]; do
if [ $nm -lt 10 ]; then
nm=0$nm
fi
wget ftp://ftp.ncdc.noaa.gov/pub/data/cmb/ersst/v5/netcdf/ersst.v5.$yr$nm.nc
nm=`expr $nm + 1`
done
yr=`expr $yr + 1`
done

cdo mergetime ersst.v5.*.nc ersst.v5.188001-202001.nc