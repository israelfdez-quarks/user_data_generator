from data_sources import HigyrusDataSource, BeCleverDataSource, AL2SyncDataSource, combine_data_sources, \
    save_to_csv


def consume_data_source(data_source):
    print(f"\nConsuming {data_source.name} data source:")

    result = data_source.to_dataframe()

    print(f"Converted to DataFrame with {len(result)} rows and {len(result.columns)} columns")

    if not result.empty:
        print("First few rows:")
        print(result.head(2))

    return result


def main():
    data_sources = [HigyrusDataSource(), BeCleverDataSource(), AL2SyncDataSource()]

    successful_sources = []
    results = []

    for data_source in data_sources:
        try:
            print(f"\nProcessing {data_source.name} data source...")
            result = consume_data_source(data_source)
            results.append(result)
            successful_sources.append(data_source)
            print(f"Successfully processed {data_source.name} data source")
        except Exception as e:
            print(f"ERROR: Failed to process {data_source.name} data source")
            print(f"Error details: {str(e)}")
            print(f"Skipping {data_source.name} and continuing with next data source")

    if not successful_sources:
        print("\nNo data sources were processed successfully. Cannot generate output.")
        return

    print("\nCombining data from all successful sources...")
    combined_result = combine_data_sources(successful_sources)

    print(f"Combined DataFrame has {len(combined_result)} rows and {len(combined_result.columns)} columns")
    print("First few rows of combined data:")
    print(combined_result.head(2))

    output_file = "users_data.csv"
    print(f"\nSaving combined data to {output_file}...")
    save_to_csv(combined_result, output_file)
    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    main()
