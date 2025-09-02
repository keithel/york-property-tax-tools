import argparse
from pathlib import Path
from fetch_property_tax import BillNotFoundException, get_tax_bill_pdf
from find_york_tax_pdf_page import find_page
from pypdf import PdfWriter
import urllib
import sys

def process_pdf(pdf_io, search_query, output):
    if search_query:
        found_page = find_page(pdf_io, search_query)
        if found_page:
            writer = PdfWriter()
            writer.add_page(found_page)
            if output:
                with open(output, "wb") as outfile:
                    writer.write(outfile)
        else:
            print(f"No page found for query '{search_query}'", file=sys.stderr)
    else:
        if output:
            with open(output, "wb") as outfile:
                outfile.write(pdf_io.read())
        else:
            sys.stdout.buffer.write(pdf_io.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Town of York Maine real estate tax pdf for a given last name, or all pages."
    )
    parser.add_argument("-s", "--search", metavar="SEARCH_QUERY", type=str,
        default=None,
        help="A last name search query used to find the desired property tax bill page.")
    parser.add_argument("-o", "--output", metavar="output-path", type=Path,
        default=None, help="Output PDF file.")
    parser.add_argument("--search-pdf", metavar="PDF_FILE", type=str,
        default=None,
        help="Provide an already downloaded PDF of all tax bills")
    args = parser.parse_args()
    search_query = args.search.lower() if args.search else None

    try:
        if args.search_pdf:
            if not search_query:
                print("Existing PDF, no search query, doing nothing.")
                sys.exit(0)

            with open(args.search_pdf, "rb") as pdf_io:
                process_pdf(pdf_io, search_query, args.output)
        else:
            tb_url = get_tax_bill_pdf()
            pages = None
            with urllib.request.urlopen(tb_url) as pdf_response:
                process_pdf(pdf_response, search_query, args.output)

    except BillNotFoundException as e:
        print(f"{str(e)}... aborting", file=sys.stderr)
    except AssertionError as e:
        print(f"{str(e)}. aborting", file=sys.stderr)
