import logging
import csv
from pathlib import Path

from tqdm import tqdm

try:
    from txt2csv.parse_args import app_arg
except ImportError:
    from parse_args import app_arg

logger: logging


def get_folder_data(input_folder: Path) -> list[Path]:
    result = []
    if input_folder.is_dir():
        # result = [item.stem for item in input_folder.glob("*.*")]
        for input_file in sorted(input_folder.glob("*.*")):
            if input_file.is_file():
                result.append(input_file)
                # input_file_stem = input_file.stem
                # result[input_file_stem] = []
                # with input_file.open("r", encoding="utf-8") as fp:
                #     while True:
                #         line = fp.readline()
                #         if not line:
                #             break
                #         input_file_row = line.strip()
                #         if input_file_row:
                #             result[input_file_stem].append(input_file_row)
    return result


def combine_files(
    input_header: list[str],
    input_data: list[Path],
    output: Path,
    input_delimiter: str = "\t",
    output_delimiter: str = ",",
    encoding="utf-8",
):
    try:
        with output.open("w", newline="", encoding=encoding) as csvfile:
            writer = csv.writer(csvfile, delimiter=output_delimiter)
            if input_header:
                writer.writerow(input_header)
            for txt_file in tqdm(input_data):
                with txt_file.open(encoding=encoding) as f:
                    reader = csv.reader(f, delimiter=input_delimiter)
                    for row in reader:
                        writer.writerow(row)
    except OSError as e:
        logger.error(f"Output data is not saved to a file: '{output}', error: {e}")
    except Exception as e:
        logger.error(f"Output data error: '{e}'")
    else:
        logger.info(f"Output data is saved to a file: '{output}'")


def proceed_file(
    txt_file: Path,
    input_header: list[str],
    output: Path,
    input_delimiter: str = "\t",
    output_delimiter: str = ",",
    encoding="utf-8",
):
    output_file = output.joinpath(txt_file.stem).with_suffix(".csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_file.open("w", newline="", encoding=encoding) as csvfile:
            writer = csv.writer(csvfile, delimiter=output_delimiter)
            if input_header:
                writer.writerow(input_header)
            with txt_file.open(encoding=encoding) as f:
                reader = csv.reader(f, delimiter=input_delimiter)
                for row in reader:
                    writer.writerow(row)
    except OSError as e:
        logger.error(
            f"proceed_file. Output data is not saved to a file: '{output_file}', error: {e}"
        )
    except Exception as e:
        logger.error(f"proceed_file. Output data error: '{e}'")
    else:
        logger.info(f"proceed_file. Output data is saved to a file: '{output_file}'")


def proceed_files(
    input_header: list[str],
    input_data: list[Path],
    output: Path,
    input_delimiter: str = "\t",
    output_delimiter: str = ",",
    encoding="utf-8",
):
    for txt_file in tqdm(input_data):
        proceed_file(
            txt_file=txt_file,
            input_header=input_header,
            output=output,
            input_delimiter=input_delimiter,
            output_delimiter=output_delimiter,
            encoding=encoding,
        )


def save_result_csv(
    input_header: list[str],
    input_data: list[Path],
    output: Path,
    input_delimiter: str = "\t",
    output_delimiter: str = ",",
    encoding="utf-8",
):
    if not input_data:
        logger.error("Nothing to save to csv file")
        return

    if not output.is_dir():
        combine_files(
            input_header=input_header,
            input_data=input_data,
            output=output,
            input_delimiter=input_delimiter,
            output_delimiter=output_delimiter,
            encoding=encoding,
        )
    else:
        proceed_files(
            input_header=input_header,
            input_data=input_data,
            output=output,
            input_delimiter=input_delimiter,
            output_delimiter=output_delimiter,
            encoding=encoding,
        )


def csv_operation(
    input_path: Path,
    output: Path,
    input_header: list[str] = None,
    input_delimiter: str = "\t",
    output_delimiter: str = ",",
):
    input_data: list[Path] = get_folder_data(input_path)
    # prepare report statistic data
    input_records = len(input_data)
    report_txt = f"{input_records=}"
    logger.info(report_txt)
    # save result to csv file
    if input_data:
        save_result_csv(
            input_header=input_header,
            input_data=input_data,
            output=output,
            input_delimiter=input_delimiter,
            output_delimiter=output_delimiter,
        )
    else:
        logger.error("No output data. Nothing to save.")


def check_absolute_path(p: Path, work: Path) -> Path | None:
    if p:
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
    input_path: Path = check_absolute_path(args.get("input"), work_path)
    output_path: Path = check_absolute_path(args.get("output"), work_path)
    headers_str: str | None = args.get("headers")
    headers_file: Path | None = check_absolute_path(args.get("headers_file"), work_path)
    headers = None
    if headers_str:
        headers = headers_str.strip().split(",")
    elif headers_file:
        headers = headers_file.read_text().strip().split(",")

    logger.debug(f"{headers=}")

    if not headers or len(headers) < 2:
        raise RuntimeError("headers is empty")

    if not output_path.exists() and output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)

    csv_operation(
        input_header=headers,
        input_path=input_path,
        output=output_path,
        input_delimiter=args.get("input_delim"),
        output_delimiter=args.get("output_delim"),
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print("Error: ", err)
