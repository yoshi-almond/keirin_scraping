from logging import exception, info
import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager import driver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

def set_gspread():
    # JSONファイルを使って認証情報を取得
    SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'keirinalert-c3d1c50d5438.json'  
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE,SCOPES) 
    # 認証情報を使ってスプレッドシートの操作権を取得
    gs = gspread.authorize(credentials)
    # 共有したスプレッドシートのキーを使ってシートの情報を取得
    SPREADSHEET_KEY = '1R2fPel8-r6A1jsg2i90TxK2RHmki_zl2GKzJvx2q-rU' 
    return gs.open_by_key(SPREADSHEET_KEY)

def output_gspread(workbook,info_list):
    worksheet = workbook.worksheet("一覧")
    #今日の日付を更新
    today = str(datetime.date.today())
    worksheet.update_acell('C2',today)
    worksheet.update_acell('F2',len(info_list))
    #古いデータをリセット
    cell_list = worksheet.range(f'D6:F200')
    for cell in cell_list:
        cell.value = ""
    worksheet.update_cells(cell_list)
    #データを書き出す
    cell_list = worksheet.range(f'D6:F{len(info_list)+5}')
    i = 0
    for item in info_list:
        cell_list[i].value = item[0]   #場所
        cell_list[i+1].value = item[1]   #ラウンド
        cell_list[i+2].value = item[2]   #締切時間
        i += 3
    worksheet.update_cells(cell_list)

class Chariloto:
    def __init__(self) -> None:
        self.driver = set_driver(True)
        self.driver.get("https://www.chariloto.com/")
        time.sleep(5)
        self.info_list = []
    def do_scraping(self):
        #競輪タブをクリック
        tab = self.driver.find_element_by_css_selector('#js-tabs')
        active_tab = tab.find_element_by_css_selector('.is-active')
        active_tab_class_name = active_tab.find_element_by_css_selector('i').get_attribute('class')
        if 'keirin' in active_tab_class_name:
            pass
        else:
            tab.find_element_by_css_selector('li:nth-child(1)').click()
            time.sleep(5)
        #各レース会場のページに移動
        all_place = tab.find_elements_by_css_selector('.keirin-tab li')
        total_place_num = len(all_place)
        #それぞれのページにアクセスして情報取得
        for i in range(total_place_num):
            try:
                #各会場へのリンクをクリック
                tab = self.driver.find_element_by_css_selector('#js-tabs')
                all_place = tab.find_elements_by_css_selector('.keirin-tab li')
                place_name = all_place[i].find_element_by_xpath('div/div/div[1]/div/div[1]').text
                all_place[i].find_element_by_xpath('div/div/div[2]/div/div[1]').click()
                time.sleep(5)
                #各ラウンドの発走時刻を取得
                race_table = self.driver.find_element_by_css_selector('.main-column > table')
                race_start_times = race_table.find_elements_by_css_selector('tr > td:nth-child(2)')
                j = 0 
                for race_start_time in race_start_times:
                    self.info_list.append([place_name,j+1,race_start_time.text])
                    j += 1
                self.driver.back()
                time.sleep(3)
            except Exception as e:
                print(e)
        self.change_to_deadline()
        return self.info_list
    def change_to_deadline(self):
        #発走時間を締切時間に変更（5分前）、チャリロトのみ使用
        for item in self.info_list:
            item[2] = datetime.datetime.strptime(item[2],'%H:%M') - datetime.timedelta(minutes=5)
            item[2] = item[2].strftime('%H:%M')
    def finish_scraping(self):
        self.driver.quit()

def main():
    #チャリロトから情報取得
    chariloto = Chariloto()
    info_list = chariloto.do_scraping()
    chariloto.finish_scraping()
    print(chariloto.info_list)

    #Googleスプレッドシートに出力
    workbook = set_gspread()
    output_gspread(workbook,info_list)

if __name__ == "__main__":
    main()