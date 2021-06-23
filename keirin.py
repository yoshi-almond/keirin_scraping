import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

LOG_FILE_PATH = "./log/log_{datetime}.log"
EXP_CSV_PATH="./exp_list_{search_keyword}_{datetime}.csv"
log_file_path=LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

def set_driver(headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(ChromeDriverManager().install(), options=options)

def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

def main():
    driver = set_driver(False)
    driver.get("http://keirin.jp/pc/top")
    time.sleep(3)
    info_list = []
    i = 1
    while True: 
        try:
            all_race = driver.find_element_by_css_selector('#kaisaiInfo_div' )
            each_race = all_race.find_element_by_css_selector(f'tr:nth-child({i})')
            each_race.find_element_by_css_selector('.live').click()
            time.sleep(3)
            place = driver.find_element_by_css_selector('#hhLblJo').text
            dento_sime = driver.find_element_by_css_selector('#hhLblShimeTime').text
            info_list.append([place,dento_sime])
            driver.back()
            time.sleep(3)
        except NoSuchElementException:
            break
        finally:
            i += 1
    print(info_list)
    
if __name__ == "__main__":
    main()
