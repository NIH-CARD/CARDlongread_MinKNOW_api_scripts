import argparse
import csv
import minknow_api
import pandas as pd
import numpy as np

# minknow_api.manager supplies "Manager" a wrapper around MinKNOW's Manager gRPC API with utilities for
# querying sequencing positions + offline basecalling tools.
from minknow_api.manager import Manager
from minknow_api.protocol_pb2 import FilteringInfo

# add in subroutine for platform qc join from CARDlongread_extract_summary_statistics Python scripts
# function for handling platform qc and calculating differences with starting active pores
def platform_qc_starting_active_pore_diff(data,platform_qc):
    # fix platform_qc column for joining
    platform_qc['Flow Cell ID'] = platform_qc['flow_cell_id']
    # join platform_qc and data tables on flow_cell_id
    data_platform_qc_join = data.join(platform_qc.set_index("flow_cell_id"),on="flow_cell_id",rsuffix='_pqc')
    # remove those where 'Flow Cell ID' is NaN
    data_platform_qc_join_cleaned = data_platform_qc_join.dropna(subset=['Flow Cell ID'])
    # exclude NaN rows after join
    # find unique run timestamps
    unique_run_timestamps = np.unique(data_platform_qc_join_cleaned["timestamp"])
    # initialize new data frame as long as unique runs based on unique run timestamps
    # remove {'Start Run Timestamp' : unique_run_timestamps} from arguments below
    data_with_platform_qc_and_diff = pd.DataFrame(columns=data_platform_qc_join_cleaned.columns.tolist() + ['Pore Difference','Time Difference'])
    # find matching rows in input platform qc table
    for idx, i in enumerate(unique_run_timestamps):
        # pick all platform qc results per run timestamp
        per_unique_run_df=data_platform_qc_join_cleaned[data_platform_qc_join_cleaned["timestamp"] == i]
        # calculate difference between platform qc and starting active pores
        per_unique_run_df.loc[:,['Pore Difference']]=abs(per_unique_run_df['total_pore_count']-per_unique_run_df['total_pore_count_pqc'])
        # calculate difference between platfrom qc and starting active pore timestamps
        per_unique_run_df.loc[:,['Time Difference']]=abs(per_unique_run_df['timestamp']-per_unique_run_df['timestamp_pqc'])
        # select per sample based on minimum time between run and platform qc check
        # get only first result if duplicates and add to table
        # below are some commands I tried and decided to ignore
        # data_with_platform_qc_and_diff.loc[idx,:]=per_unique_run_df[per_unique_run_df['Time Difference']==min(per_unique_run_df['Time Difference'])].iloc[0,:]
        # append deprecated in pandas 2.0
        # data_with_platform_qc_and_diff = data_with_platform_qc_and_diff.append(per_unique_run_df[per_unique_run_df['Time Difference']==min(per_unique_run_df['Time Difference'])].iloc[0,:])
        # below for debugging
        # print(per_unique_run_df)
        data_with_platform_qc_and_diff.loc[idx] = per_unique_run_df[per_unique_run_df['Time Difference']==min(per_unique_run_df['Time Difference'])].iloc[0,:]
    # convert starting active pore column to numeric
    # data_with_platform_qc_and_diff.loc[:,['Starting Active Pores']]=pd.to_numeric(data_with_platform_qc_and_diff['Starting Active Pores'])
    # return data frame with platform qc active pores, pore differences, and timestamp differences appended
    return data_with_platform_qc_and_diff

def main():
    """Main entrypoint for list_mux_scan example"""
    parser = argparse.ArgumentParser(
        description="List first mux scan results for all sequencing positions."
    )
    parser.add_argument(
        "--host", default="localhost", help="Specify which host to connect to."
    )
    parser.add_argument(
        "--port", default=None, help="Specify which port to connect to."
    )
    parser.add_argument(
        "--position", default=None, help="Specify which position to connect to."
    )
    parser.add_argument(
        "--api-token",
        default=None,
        help="Specify an API token to use, should be returned from the sequencer as a developer API token.",
    )
    parser.add_argument(
        "--platform-qc",
        default=None,
        help="Specify platform QC csv input for comparison against mux scan results to calculate pore dropoffs.",
    )
    parser.add_argument(
        "--platform-qc-output",
        default=None,
        help="Specify csv output for platform QC comparison result against mux scan results to calculate pore dropoffs.",
    )

    parser.add_argument(
        "output_name",
        help="Name of an output file to write csv mux scan results to.",
    )

    args = parser.parse_args()
    
    # check if output file provided
    if args.output_name is None:
        quit('ERROR: No output filename (output_name) provided!')

    # Construct a manager using the host + port provided.
    manager = Manager(
        host=args.host, port=args.port, developer_api_token=args.api_token
    )

    # Iterate all sequencing positions:
    results = []
    found_position = False
    for pos in manager.flow_cell_positions():
        # only count running positions
        if not pos.running:
            continue

        # Ignore positions if requested:
        if args.position and args.position != pos.name:
            continue

        # Dump all pqc protocols run on the position:
        found_position = True
        pos_connection = pos.connect()
        # position: pos.name
        # flow cell ID: pos_connection.device.get_flow_cell_info().flow_cell_id
        # position acquisition info: pos_acquisition_info=pos_connection.acquisition.get_acquisition_info()
        # single pores: pos_acquisition_info.bream_info.mux_scan_results[0].counts['single_pore']
        # reserved pores: pos_acquisition_info.bream_info.mux_scan_results[0].counts['reserved_pore']
        # total active pores: single pores + reserved pores
        # timestamp: pos_acquisition_info.start_time.seconds
        
        # current_mux_scan = pos_connection.acquisition.append_mux_scan_result()
        # protocols = pos_connection.protocol.list_protocol_runs(
        #    filter_info=FilteringInfo(pqc_filter=FilteringInfo.PlatformQcFilter())
        # )
        print(f"Searching position {pos.name}")
        # get PROM ID
        prom_id=pos_connection.instance.get_machine_id().machine_id
        # get position acquisition info
        pos_acquisition_info=pos_connection.acquisition.get_acquisition_info()
        
        # get single pores and reserved pores from first mux scan (index 0)
        mux_scan_results = pos_acquisition_info.bream_info.mux_scan_results
        if len(mux_scan_results) >= 1:
            first_mux_scan = mux_scan_results[0]
            single_pores = first_mux_scan.counts['single_pore']
            reserved_pores = first_mux_scan.counts['reserved_pore']
            # total pore count is single_pores + reserved_pores
            total_pore_count = single_pores + reserved_pores
            # get mux scan time stamp
            mux_scan_timestamp = first_mux_scan.mux_scan_timestamp
            # add results for current position
            results.append(
                    {
			"prom_id": prom_id,
                        "position": pos.name,
                        "flow_cell_id": pos_connection.device.get_flow_cell_info().flow_cell_id,
                        "total_pore_count": total_pore_count,
			"mux_scan_timestamp": mux_scan_timestamp,
			"timestamp": pos_acquisition_info.start_time.seconds
                    }
                )
    # add in platform QC information and calculate pore dropoffs if specified
    if args.platform_qc is not None:
        platform_qc_table=pd.read_csv(args.platform_qc)
        results_df=pd.DataFrame(results)
        results_with_platform_qc=platform_qc_starting_active_pore_diff(results_df,platform_qc_table)
        if args.platform_qc_output is not None:
            results_with_platform_qc.to_csv(args.platform_qc_output, index=False)
        else:
            quit('ERROR: No output filename (--platform-qc-output) provided!')
            

    with open(args.output_name, "w") as csvfile:
        result_writer = csv.DictWriter(
            csvfile,
            ["prom_id", "position", "flow_cell_id", "total_pore_count", "mux_scan_timestamp", "timestamp"],
        )

        result_writer.writeheader()
        for result in results:
            result_writer.writerow(result)

    if not found_position and args.position:
        print(f"Failed to locate sequencing position: {args.position}")
        exit(1)


if __name__ == "__main__":
    main()
