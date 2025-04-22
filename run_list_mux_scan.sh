#!/bin/bash
# first argument was platform qc file
# now get newest platform qc file
# ls -Art excludes . and .., reverses sort order, and sorts by time
newest_platform_qc=$(ls -Art platform_qc_extract_all_proms*.csv | tail -n 1)
# get date
current_date=$(date +"%m%d%Y")
# set PROM
PROM="prom002"
# print out mux scan info if under 6000 pores at start of sequencing
# changed in most recent version - give mux scan info if 1500 pore loss or greater
/opt/ont/minknow/ont-python/bin/python list_mux_scan.py --platform-qc ${newest_platform_qc} --platform-qc-output first_mux_scan_with_platform_qc_extract_${PROM}_${current_date}.csv first_mux_scan_${PROM}_${current_date}.csv
# print header and any mux scans with over a 1500 pore dropoff
awk -F',' '{if(NR==1 || $13>1500) print $0}' first_mux_scan_with_platform_qc_extract_${PROM}_${current_date}.csv > first_mux_scan_with_platform_qc_extract_1500_dropoff_${PROM}_${current_date}.csv
# open up output in libreoffice
# libreoffice --calc --infilter='Text - txt - csv (StarCalc)':44,34,0,1 platform_qc_extract_prom002_121024.csv
# copy output to samba share
cp first_mux_scan*${PROM}*${current_date}.csv /srv/samba/share
# print over 1500 pore dropoff to stdout
cat first_mux_scan_with_platform_qc_extract_1500_dropoff_${PROM}_${current_date}.csv 

