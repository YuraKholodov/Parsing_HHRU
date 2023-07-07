import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
import json

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
}


def get_source_html(url, driver):
    driver.get(url)
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)


def get_all_vacancys(class_):
    with open("index.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    return soup.find_all(class_=class_)


def filter_vacancy(all_vacancys, pattern):
    project_data = []
    for vacancy in all_vacancys:
        if re.findall(pattern, vacancy.text):
            req = requests.get(vacancy.get("href"), headers=headers).text
            href = vacancy.get("href")
            soup = BeautifulSoup(req, "lxml")
            try:
                company_name = (
                    soup.find("div", class_="vacancy-company-redesigned")
                    .find(class_="bloko-header-section-2 bloko-header-section-2_lite")
                    .text
                )
            except Exception:
                company_name = "Компания не указана"

            try:
                city = (
                    soup.find("div", class_="vacancy-company-redesigned").find("p").text
                )
            except Exception:
                city = "Город не указан"

            try:
                salary = soup.find(
                    "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
                )
                if re.findall(r"[₽$]", salary.text):
                    salary = salary.text
                else:
                    salary = "Зарплата не указана"
            except Exception:
                salary = "Зарплата не указана"

            project_data.append(
                {
                    "href": href,
                    "salary": salary,
                    "city": city,
                    "company_name": company_name,
                }
            )
    return project_data


def add_json(data_list):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)


def main():
    get_source_html(url=url, driver=driver)
    all_vacancys = get_all_vacancys(class_="serp-item__title")
    data = filter_vacancy(all_vacancys, pattern="[Jj]unior|[Ff]lask")
    add_json(data)


if __name__ == "__main__":
    main()
