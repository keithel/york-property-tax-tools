from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys

DEBUG = False


class BillNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def print_debug(str):
    if DEBUG:
        print(str)

def get_tax_bill_pdf():
    driver = webdriver.Chrome()
    driver.get("https://www.yorkmaine.org/DocumentCenter")

    t_in_spans = driver.find_elements(by = By.CSS_SELECTOR, value = "span.t-in")
    print_debug(f"len(t_in_spans) == {len(t_in_spans)}")
    tax_collector_spans = [span for span in t_in_spans if "tax collector" in span.text.lower()]
    print_debug(f"len(tax_collector_spans) == {len(tax_collector_spans)}")
    assert len(tax_collector_spans) == 1
    tax_collector_span = tax_collector_spans[0]

    parent_t_item = tax_collector_span.find_element(by = By.XPATH, value = "../..")
    print_debug(f"parent_t_item.tag_name == {parent_t_item.tag_name}")
    assert parent_t_item.tag_name == "li"
    parent_t_item.click()
    # It would be better if this did not rely on timer based waits to function,
    # as it can be unreliable.
    time.sleep(0.2)

    t_in_spans = parent_t_item.find_elements(by = By.CSS_SELECTOR, value = "span.t-in")
    print_debug(f"len(t_in_spans) == {len(t_in_spans)}")
    for s in t_in_spans:
        print_debug(f"s.text == {s.text}")
    tax_bills_spans = [span for span in t_in_spans if "tax bills" in span.text.lower()]
    print_debug(f"len(tax_bills_spans) == {len(tax_bills_spans)}")
    assert len(tax_bills_spans) == 1

    tax_bills_span = tax_bills_spans[0]
    tax_bills_item = tax_bills_span.find_element(by = By.XPATH, value = "../..")
    tax_bills_item.click()

    time.sleep(0.2)

    cur_year = time.localtime().tm_year
    fetch_tax_year = cur_year+1

    a_pdfs = driver.find_elements(by = By.CLASS_NAME, value = "pdf")
    desired_pdfs = [ pdf for pdf in a_pdfs if str(fetch_tax_year) in pdf.text ]

    if len(desired_pdfs) <= 0:
        raise BillNotFoundException(f"No property tax bill document found for {fetch_tax_year}")

    assert len(desired_pdfs) == 1
    desired_pdf = desired_pdfs[0]

    assert f"{fetch_tax_year} tax bills" == desired_pdf.text.lower()
    return desired_pdf.get_attribute("href")
