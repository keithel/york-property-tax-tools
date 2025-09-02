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
    print_debug("Starting Chrome webdriver")
    driver = webdriver.Chrome()
    print_debug(f"Window size: {driver.get_window_size()}")
    driver.set_window_size(1280, 1024)
    print_debug(f"Changed window size to: {driver.get_window_size()}")
    url = "https://www.yorkmaine.org/DocumentCenter"
    driver.get(url)
    print_debug(f"Loaded {url}")
    time.sleep(1.0)

    tree_node_content_wrappers = driver.find_elements(by = By.CLASS_NAME, value = "ant-tree-node-content-wrapper")
    print_debug(f"len(tree_node_content_wrappers) == {len(tree_node_content_wrappers)}")
    tax_collector_nodes = [node for node in tree_node_content_wrappers if "tax collector" in node.text.lower()]
    print_debug(f"len(tax_collector_nodes) == {len(tax_collector_nodes)}")
    if len(tax_collector_nodes) != 1:
        raise BillNotFoundException(f"Unexpected number of tax collector nodes: {len(tax_collector_nodes)}")
    tax_collector_node = tax_collector_nodes[0]
    print_debug("Found tax collector node")

    tax_collector_parent = tax_collector_node.find_element(by = By.XPATH, value = "..")
    print_debug(f"tax_collector_parent.tag_name == {tax_collector_parent.tag_name}")
    if tax_collector_parent.tag_name != "div":
        raise BillNotFoundException("Website layout changed!")
    switchers = tax_collector_parent.find_elements(by = By.CSS_SELECTOR, value = "span.ant-tree-switcher")
    print_debug(f"Found {len(switchers)} tax collector switch spans")
    switcher = switchers[0]
    switcher.click()
    # It would be better if this did not rely on timer based waits to function,
    # as it can be unreliable.
    time.sleep(0.2)
    print_debug("Clicked tax collector node")

    parent_parent = tax_collector_parent.find_element(by = By.XPATH, value = "..")
    tree_node_content_wrappers = parent_parent.find_elements(by = By.CSS_SELECTOR, value = "span.ant-tree-node-content-wrapper")
    print_debug(f"len(tree_node_content_wrappers) == {len(tree_node_content_wrappers)}")
    tax_bills_node = None
    for s in tree_node_content_wrappers:
        # print_debug(f"s.text == {s.text}")
        if "tax bills" in s.text.lower():
            tax_bills_node = s
            break
    if not tax_bills_node:
        raise BillNotFoundException('"Tax Bills" tree node not found.')
    print_debug("Found tax bills node")

    tax_bills_node.click()
    print_debug("Clicked tax bills node")

    time.sleep(1.0)

    cur_year = time.localtime().tm_year
    fetch_tax_year = cur_year+1

    a_pdfs = driver.find_elements(by = By.CLASS_NAME, value = "pdf")
    desired_pdfs = [ pdf for pdf in a_pdfs if str(fetch_tax_year) in pdf.text ]
    print_debug(f"Found {len(desired_pdfs)} pdfs")

    if len(desired_pdfs) <= 0:
        raise BillNotFoundException(f"No property tax bill document found for {fetch_tax_year}")

    if len(desired_pdfs) > 1:
        raise BillNotFoundException(f"{len(desired_pdfs)} pdfs found -- don't know which one to search!")
    desired_pdf = desired_pdfs[0]

    if f"{fetch_tax_year} tax bills" != desired_pdf.text.lower():
        print_debug(f"Unexpected PDF link name {desired_pdf.text}")

    print_debug(f'Found "{desired_pdf.text}", returning {desired_pdf.get_attribute("href")}.')
    return desired_pdf.get_attribute("href")
