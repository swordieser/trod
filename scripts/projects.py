from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import logging
from dataclasses import dataclass, asdict
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__file__)

PROJECTS_LINK = "https://dobro.mail.ru/projects/?recipient="
PROJECTS_TAGS = ["culture", "nature", "animals"]


@dataclass
class Project:
    name: str
    fund_name: str
    city: str | None
    end_date: str | None
    money_collected: int
    money_needed: int
    main_text: str | None
    text_about: str | None
    # tag: str

    @property
    def percentage(self):
        if self.money_collected >= self.money_needed:
            return "100%"
        else:
            return f"{int((self.money_collected / self.money_needed) * 100)}%",


def setup_driver() -> WebDriver:
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def driver_wait(chrome_driver):
    wait = WebDriverWait(chrome_driver, 10)
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")


def _process_money_bar(s: str):
    return list(map(
        int,
        s.replace("Собранная сумма: ", "")
        .replace(" руб.", "")
        .split(" из ")
    ))


def get_project_information_by_link(chrome_driver: WebDriver, link: str, project_tag: str = "") -> Project:
    chrome_driver.get(link)
    driver_wait(chrome_driver)

    div_main_content = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'project-box_mainContent')]")
    city, end_date = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'project-box_itemInfo')]").text.split(
        "\n")
    name = div_main_content.find_element(By.TAG_NAME, "h1").text
    fund_name = div_main_content.find_element(By.TAG_NAME, "a").text

    money_bar = chrome_driver.find_element(By.XPATH, "//span[contains(text(),'Собранная сумма')]")
    chrome_driver.execute_script("arguments[0].setAttribute('class', '')", money_bar)
    driver_wait(chrome_driver)
    money_collected, money_needed = _process_money_bar(money_bar.text)

    project = Project(
        name=name,
        fund_name=fund_name,
        city=city,
        end_date=end_date,
        money_collected=money_collected,
        money_needed=money_needed,
        main_text=chrome_driver.find_element(By.XPATH, "//div[contains(@class,'project-box_mainText')]").text,
        text_about=chrome_driver.find_element(By.XPATH, "//div[contains(@class,'about-project_about')]").text,
        # tag=project_tag
    )

    return project


def collect_projects_links_from_page_by_tag(chrome_driver: WebDriver, project_tag: str) -> set[str]:
    link = f"{PROJECTS_LINK}{project_tag}"
    chrome_driver.get(link)
    driver_wait(chrome_driver)

    card_list = chrome_driver.find_element(By.XPATH, "//div[contains(@class,'styles_cardListContainer')]")

    result = []
    for a in card_list.find_elements(By.TAG_NAME, "a"):
        link = a.get_attribute("href")
        if link.startswith("https://dobro.mail.ru/"):
            result.append(link.replace("?action=help_money", ""))

    return set(result)


def collect_projects():
    driver = setup_driver()

    projects = []

    for tag in PROJECTS_TAGS:
        project_links = collect_projects_links_from_page_by_tag(driver, tag)
        for link in project_links:
            projects.append(get_project_information_by_link(driver, link, tag))

    return projects


def collect_projects_by_links(links: list[str]):
    result = []
    driver = setup_driver()

    for link in links:
        result.append(get_project_information_by_link(driver, link))

    return result


def dump_projects_to_csv(links: list[str]):
    projects = collect_projects_by_links(links)

    df = pd.DataFrame([asdict(project) for project in projects])

    df_project = df[["name", "fund_name", "city", "end_date", "money_collected", "money_needed", "main_text", "text_about"]]

    df_project.to_csv('project.csv', encoding='utf-8')
