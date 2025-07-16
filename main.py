from data_sources import HigyrusDataSource, MockDataSource, combine_data_sources, save_to_csv


def consume_data_source(data_source):
    print(f"\nConsuming {data_source.name} data source:")

    result = data_source.to_dataframe()

    print(f"Converted to DataFrame with {len(result)} rows and {len(result.columns)} columns")

    if not result.empty:
        print("First few rows:")
        print(result.head(2))

    return result


def main():
    try:
        data_sources = [HigyrusDataSource(), MockDataSource()]

        results = []
        for data_source in data_sources:
            result = consume_data_source(data_source)
            results.append(result)

        print("\nCombining data from all sources...")
        combined_result = combine_data_sources(data_sources)

        print(f"Combined DataFrame has {len(combined_result)} rows and {len(combined_result.columns)} columns")
        print("First few rows of combined data:")
        print(combined_result.head(2))

        output_file = "users_data.csv"
        print(f"\nSaving combined data to {output_file}...")
        save_to_csv(combined_result, output_file)
        print(f"Data saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
