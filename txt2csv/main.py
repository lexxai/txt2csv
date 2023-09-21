import logging
import csv
from pathlib import Path

try:
    from txt2csv.parse_args import app_arg
except ImportError:
    from parse_args import app_arg

logger: logging


def get_folder_data(input_folder: Path) -> dict[str, list[str]]:
    result = {}
    if input_folder.is_dir():
        # result = [item.stem for item in input_folder.glob("*.*")]
        for input_file in input_folder.glob("*.*"):
            if input_file.is_file():
                input_file_stem = input_file.stem
                result[input_file_stem] = []
                with input_file.open("r", encoding="utf-8") as fp:
                    while True:
                        line = fp.readline()
                        if not line:
                            break
                        input_file_row = line.strip()
                        if input_file_row:
                            result[input_file_stem].append(input_file_row)
    return result


def save_result_csv(
    input_header: list[str],
    input_data: dict[str, list[str]],
    output: Path,
    delimiter=",",
    encoding="utf-8",
):
    if not input_data:
        logger.error("Nothing to save to csv file")
        return

    try:
        with output.open("w", newline="", encoding=encoding) as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            if input_header:
                writer.writerow(input_header)
            for key in input_data.keys():
                row: list = [key]
                row.extend(input_data[key])
                writer.writerow(row)
    except OSError as e:
        logger.error(f"Output data is not saved to a file: '{output}', error: {e}")
    else:
        logger.info(f"Output data is saved to a file: '{output}'")


def csv_operation(input_path: Path, output: Path, input_header: list[str] = None):
    input_data: dict[str, list[str]] = get_folder_data(input_path)
    # prepare report statistic data
    input_records = len(input_data)
    report_txt = f"{input_records=}"
    logger.info(report_txt)
    # save result to csv file
    if input_data:
        save_result_csv(input_header, input_data, output)
    else:
        logger.error("No output data. Nothing to save.")


def check_absolute_path(p: Path, work: Path) -> Path:
    return p if p.is_absolute() else work.joinpath(p)


def main():
    global logger
    args = app_arg()
    logging.basicConfig(
        level=logging.DEBUG if args.get("verbose") else logging.INFO,
        format="%(asctime)s  %(message)s",
    )
    logger = logging.getLogger(__name__)
    work_path = args.get("work")
    input_path = check_absolute_path(args.get("input"), work_path)
    output_path = check_absolute_path(args.get("output"), work_path)
    headers_str: str = args.get("headers")
    headers = None
    if headers_str:
        headers = headers_str.strip().split(",")
    csv_operation(input_path, output_path, headers)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
