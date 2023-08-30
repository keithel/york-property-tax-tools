import argparse
from pathlib import Path
from fetch_property_tax import BillNotFoundException, get_tax_bill_pdf
from find_york_tax_pdf_page import find_page
from pypdf import PdfWriter
import urllib
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", metavar="COMMAND", type=str, default="url",
        nargs="?",
        help="A command, one of 'url' or 'get'. If unspecified, 'url' is "
        "implied.\r"
        "    url - Print the URL to the current tax year's taxes.\r"
        "    get - Fetch and output all property taxes for the year given (or "
        "          current year if not specified). If no name or address "
        "          specified, will output all property tax bills.")
    parser.add_argument("-s", "--search", metavar="SEARCH_QUERY", type=str,
        default=None,
        help="A search query used to find the desired property tax bill page.")
    parser.add_argument("-o", "--output", metavar="output-path", type=Path,
        default=None, help="Output PDF file.")
    args = parser.parse_args()
    cmd = args.command
    search_query = args.search.lower() if args.search else None

    try:
        tb_url = get_tax_bill_pdf()

        pages = None
        with urllib.request.urlopen(tb_url) as pdf_file:
            writer = PdfWriter()
            if search_query:
                writer.add_page(find_page(pdf_file, search_query))
                if args.output:
                    with open(args.output, "wb") as outfile:
                        writer.write(outfile)
                        writer.close()
                else:
                    writer.write(sys.stdout)
            elif args.output:
                with open(args.output, "wb") as outfile:
                    outfile.write(pdf_file.read())
            else:
                sys.stdout.buffer.write(pdf_file.read())

    except BillNotFoundException as e:
        print(f"{str(e)}... aborting", file=sys.stderr)
    except AssertionError as e:
        print(f"{str(e)}. aborting", file=sys.stderr)
