from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import csv

options = Options()
options.add_argument('start-maximized')


driver = webdriver.Chrome(options=options) # используем Chrome, запускаем ссылку
driver.get("https://www.wildberries.ru/")

wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
element.send_keys('книги программирование') # вводим поисковый запрос
element.send_keys(Keys.ENTER)
time.sleep(5)

i = 1
# извлечем книги из первых 4 страниц
books = []
while i <= 4:
    # прокручиваем страницу до конца и получаем все ссылки на книги
    while True:
        books_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@id]')))
        count = len(books_cards)
        driver.execute_script('window.scrollBy(0, 1800)')  
        time.sleep(3)
        books_cards = driver.find_elements(By.XPATH, '//article[@id]')
        if len(books_cards) == count:
            break

    url_list = [card.find_element(By.XPATH, './div/a').get_attribute('href') for card in books_cards]
    driver_1 = webdriver.Chrome(options=options)
    wait_1 = WebDriverWait(driver_1, 20)
    # переходим по каждой ссылке и парсим нужные данные (название, цена, url)
    for book in url_list:
        book_dict = {}
        driver_1.get(book)
        book_dict['name'] = wait_1.until(EC.presence_of_element_located((By.XPATH, "//h1"))).text
        price = wait_1.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div/div/div/p/span/ins')))
        try:
            book_dict['price'] = float(re.sub(r'[^\d.]+', '', price.text)) 
        except Exception:
            book_dict['price'] = None
        book_dict['url'] = book
        books.append(book_dict)
    # переходим на следующую страницу
    try:
        next = driver.find_element(By.XPATH, '//*[@id="catalog"]/div/div[5]/div/a[@class="pagination-next pagination__next j-next-page"]')
        next.click()
        i += 1
        time.sleep(10)
    except:
        break


# сохраняем данные в csv-файлы
with open('books.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Название', 'Цена', 'URL'])
    for book_dict in books:
        writer.writerows([book_dict.values()])