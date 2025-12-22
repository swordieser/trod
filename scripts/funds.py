from projects import setup_driver, driver_wait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import logging
from dataclasses import dataclass

logger = logging.getLogger(__file__)

FUNDS_LINK = "https://dobro.mail.ru/sos/?recipient="
FUNDS_TAGS = ["culture", "nature", "animals"]


@dataclass
class Fund:
    name: str
    phone: str | None
    url: str | None
    tags: list[str]
    description: str
    stats: list[str]
    projects: list[str]


def _process_money_bar(s: str):
    return list(map(
        int,
        s.replace("Собранная сумма: ", "")
        .replace(" руб.", "")
        .split(" из ")
    ))


def get_fund_information_by_link(chrome_driver: WebDriver, link: str, fund_tag: str) -> Fund:
    chrome_driver.get(link)
    driver_wait(chrome_driver)

    div_main_info = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'fund-info_container')]")
    div_stats_info = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'fund-info-stats_container')]")
    div_fund_projects = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'fund-projects_cards')]")

    fund_name = div_main_info.find_element(By.TAG_NAME, "h1").text
    try:
        fund_phone = div_main_info.find_element(By.XPATH, "//a[contains(@class,'fund-info_phone')]").text
    except:
        fund_phone = None

    try:
        fund_url = div_main_info.find_element(By.XPATH, "//a[contains(@class,'fund-info_link')]").text
    except:
        fund_url = None

    fund_tags = div_main_info.find_element(By.XPATH, "//div[contains(@class,'fund-info_recipients')]").text.split("\n")
    fund_description = div_main_info.find_element(By.XPATH, "//div[contains(@class,'fund-info_description')]").text.replace("\nПодробнее", "")

    divs_stats = div_stats_info.find_elements(By.XPATH, "//div[contains(@class,'fund-info-stats-item_container')]")
    fund_stats = [d.text.replace("\n", " ") for d in divs_stats]

    a_projects = div_fund_projects.find_elements(By.TAG_NAME, "a")
    fund_projects = list(set(a.get_attribute("href").replace("?action=help_money", "") for a in a_projects))

    fund = Fund(
        name=fund_name,
        phone=fund_phone,
        url=fund_url,
        tags=fund_tags,
        description=fund_description,
        stats=fund_stats,
        projects=fund_projects
    )

    return fund


def collect_funds_links_from_page_by_tag(chrome_driver: WebDriver, fund_tag: str) -> set[str]:
    link = f"{FUNDS_LINK}{fund_tag}"
    chrome_driver.get(link)
    driver_wait(chrome_driver)

    card_list = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'sos_cards')]")

    result = []
    for a in card_list.find_elements(By.XPATH, ".//div/div/a"):
        link = a.get_attribute("href")
        if "/funds/" in link:
            result.append(link)

    return set(result)


def collect_funds():
    driver = setup_driver()

    funds = []

    for tag in FUNDS_TAGS:
        fund_links = collect_funds_links_from_page_by_tag(driver, tag)
        for link in fund_links:
            funds.append(get_fund_information_by_link(driver, link, tag))

    return funds



