# NIA CARD Long Read MinKNOW API Scripts
This repository includes Python scripts the CARD long read team uses to query data from the MinKNOW API on its three PromethION sequencers. The included scripts collect all past platform QC flow cell checks and identify the first mux scan for runs currently sequencing on a PromethION instrument.
## Usage
All scripts below should be run on PromethIONs themselves using the python executable provided at ```/opt/ont/minknow/ont-python/bin/python```.
```
usage: list_platform_qc.py [-h] [--host HOST] [--port PORT] [--position POSITION] [--api-token API_TOKEN] output_name

List historical flow cell checks on a host.

positional arguments:
  output_name           Name of an output file to write csv platform qc results to.

options:
  -h, --help            show this help message and exit
  --host HOST           Specify which host to connect to.
  --port PORT           Specify which port to connect to.
  --position POSITION   Specify which position to connect to.
  --api-token API_TOKEN
                        Specify an API token to use, should be returned from the sequencer as a developer API token.
```
```
usage: list_mux_scan.py [-h] [--host HOST] [--port PORT] [--position POSITION] [--api-token API_TOKEN] [--platform-qc PLATFORM_QC] [--platform-qc-output PLATFORM_QC_OUTPUT] output_name

List first mux scan results for all sequencing positions.

positional arguments:
  output_name           Name of an output file to write csv mux scan results to.

options:
  -h, --help            show this help message and exit
  --host HOST           Specify which host to connect to.
  --port PORT           Specify which port to connect to.
  --position POSITION   Specify which position to connect to.
  --api-token API_TOKEN
                        Specify an API token to use, should be returned from the sequencer as a developer API token.
  --platform-qc PLATFORM_QC
                        Specify platform QC csv input for comparison against mux scan results to calculate pore dropoffs.
  --platform-qc-output PLATFORM_QC_OUTPUT
                        Specify csv output for platform QC comparison result against mux scan results to calculate pore dropoffs.
```
## Example platform QC output
```
position,flow_cell_id,product_code,passed,total_pore_count,timestamp
1A,PBA58162,FLO-PRO114M,True,5711,1738685101
1A,PBC70863,FLO-PRO114M,True,8754,1741107629
1A,PAW64396,FLO-PRO114M,True,7918,1715692853
1A,PAY03975,FLO-PRO114M,False,4639,1719841913
1A,PAS46279,FLO-PRO114M,True,7254,1698170521
1A,PAW73240,FLO-PRO114M,True,8692,1716920359
1A,PAY16839,FLO-PRO114M,True,5901,1732215050
1A,PAS46462,FLO-PRO114M,True,5393,1712240576
1A,PAU50576,FLO-PRO114M,True,5702,1709649386
1A,PAW22538,FLO-PRO114M,False,2865,1720724103
1A,PAW40284,FLO-PRO114M,True,7493,1716310158
1A,PAW97606,FLO-PRO114M,False,1843,1742327532
1A,PAU57082,FLO-PRO114M,True,6941,1710172035
1A,PAY13333,FLO-PRO114M,True,6479,1730745897
1A,PAW60658,FLO-PRO114M,True,6837,1715696185
1A,PBA64277,FLO-PRO114M,True,6768,1734383005
1A,PAU30477,FLO-PRO114M,True,6724,1704822302
1A,PAW69882,FLO-PRO114M,True,6316,1720789987
1A,CTC42338,FLO-PRO002,False,0,1724772707
```
