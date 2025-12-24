from projects import setup_driver, driver_wait, dump_projects_to_csv
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import logging
from dataclasses import dataclass, asdict
import pandas as pd

logger = logging.getLogger(__file__)

FUNDS_LINK = "https://dobro.mail.ru/sos/?recipient="
FUNDS_TAGS = ["culture", "nature", "animals"]

map_tag_to_id = {
    "Животные": 0,
    "Культура": 1,
    "Природа": 2,
    "Дети": 3,
    "Взрослые": 4,
    "Пожилые": 5
}


@dataclass
class Fund:
    name: str
    phone: str | None
    url: str | None
    tags: list[str]
    description: str
    total_collected: int
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

    try:
        div_fund_projects = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'fund-projects_cards')]")
    except:
        div_fund_projects = None

    fund_name = div_main_info.find_element(By.TAG_NAME, "h1").text
    try:
        fund_phone = div_main_info.find_element(By.XPATH, "//a[contains(@class,'fund-info_phone')]").text
    except:
        fund_phone = None

    try:
        fund_url = div_main_info.find_element(By.XPATH, "//a[contains(@class,'fund-info_link')]").text
    except:
        fund_url = None

    fund_tags = (
        div_main_info
        .find_element(By.XPATH, "//div[contains(@class,'fund-info_recipients')]")
        .text
        .split("\n")
    )

    fund_description = (
        div_main_info
        .find_element(By.XPATH, "//div[contains(@class,'fund-info_description')]")
        .text
        .replace("\nПодробнее", "")
    )

    divs_stats = div_stats_info.find_elements(By.XPATH, "//div[contains(@class,'fund-info-stats-item_container')]")
    fund_stats = [d.text.replace("\n", " ") for d in divs_stats]

    if div_fund_projects:
        a_projects = div_fund_projects.find_elements(By.TAG_NAME, "a")
        fund_projects = list(set(a.get_attribute("href").replace("?action=help_money", "") for a in a_projects))
    else:
        fund_projects = []

    fund = Fund(
        name=fund_name,
        phone=fund_phone,
        url=fund_url,
        tags=fund_tags,
        description=fund_description,
        total_collected=int(fund_stats[-1].replace(" ₽ собрано на работу фонда", "").replace(" ", "")),
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


def dump_funds_to_csv(funds: list[Fund]):
    df = pd.DataFrame([asdict(fund) for fund in funds])

    df_funds: pd.DataFrame = df[["name", "description", "total_collected", "phone", "url"]]
    df_tags: pd.DataFrame = df[["name", "tags"]]

    df_funds = df_funds.drop_duplicates(subset="name")
    df_tags = df_tags.drop_duplicates(subset="name")

    for idx, row in df_funds.iterrows():
        df_tags.loc[df_tags['name'] == row["name"], 'name'] = idx

    df_tags.rename(columns={"name": "fund_id", "tags": "tag_id"}, inplace=True)
    df_tags = df_tags.explode("tag_id")
    df_tags["tag_id"] = df_tags["tag_id"].apply(lambda tag: map_tag_to_id[tag])

    df_funds.to_csv('funds.csv', encoding='utf-8', index_label="id")
    df_tags.to_csv('funds_tags.csv', encoding='utf-8', index=False)


def collect_everything():
    funds = collect_funds()
    dump_funds_to_csv(funds)
    dump_projects_to_csv(funds)


collect_everything()
