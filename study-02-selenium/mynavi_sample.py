import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
# 処理待機用
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import datetime

# Chromeを起動する関数
INFO = 1
ERROR = 2

def set_driver(driver_path, headless_flg):
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
    # 課題8 Chromeドライバーを自動で更新
    return Chrome(ChromeDriverManager().install(), options=options)

# main処理


def main():
    # 課題4 任意のキーワードをコンソールから指定
    search_keyword =input("求人検索のキーワードを入力してください。 >>> ")
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    __write_log("ホームページを開きます。", INFO)
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
 
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
    
    # 課題7 ログファイルの出力
    __write_log("検索を開始します。", INFO)
    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    # ページ終了まで繰り返し取得
    exp_name_list = []
    # 検索結果の一番上の会社名を取得
    # name_list = driver.find_elements_by_class_name("cassetteRecruit__name")

    __write_log("検索結果の情報を取得します。", INFO)
    # 課題3 2ページ以降も取得する
    while True:
            
        # 検索結果の会社ごとのコンテンツを取得
        try:
            WebDriverWait(driver, 30).until(
                # 全ての要素が読み込まれるまで待機
                EC.presence_of_all_elements_located
            )
            name_list = driver.find_elements_by_class_name("cassetteRecruit__content")
        except:
            __write_log("検索結果を取得できませんでした。", ERROR)
            return

        # 課題2 for分を取得
        # 1ページ分繰り返し
        for company_element in name_list:
            cur_list = []
            company_name = company_element.find_element_by_class_name("cassetteRecruit__name").text
            
            try:
                __write_log("{}: ホームぺージの情報を取得します。".format(company_name), INFO)
                # 各社の情報を取得し、リストに追加する
                __add_companyinfo_to_list(cur_list, company_element)

            # 課題6 エラー発生時にスキップして処理を継続する
            except:
                __write_log("{}: ホームぺージの情報を取得中にエラーが発生しました。".format(company_name), ERROR)
            finally:
                exp_name_list.append(cur_list)

        # 課題3 2ページ以降の情報も取得
        # 次ページボタンがあれば押下する
        try:
            next_page = driver.find_element_by_class_name("iconFont--arrowLeft")
            driver.execute_script("window.scrollTo(0, " + str(next_page.location.get('y')) + ");")
            next_page.click()
        except:
            __write_log("次のページへ遷移する際にエラーが発生しました。", ERROR)
            break
    
    # 課題5 pandasでCSV出力
    df = pd.DataFrame(exp_name_list)
    df.to_csv("output.csv")


def __write_log(text: str, log_level: int):
    
    # ログレベルの記載
    log_lev = ""
    if log_level == ERROR:
        log_lev = "[ERROR]"
    elif log_level == INFO:
        log_lev = "[INFO]"

    with open('logs.txt', 'a', encoding='UTF-8') as file:
        file.write("{log}[{dt}] {text} \n".format(
            log=log_lev,
            dt=datetime.datetime.now(),
            text=text
            ))

def __add_companyinfo_to_list(cur_list: list, company_element: any):
    """会社の情報を引数のリストに追加する"""
    # 会社名を取得
    head_contents = company_element.find_element_by_class_name("cassetteRecruit__name")
    company_name = head_contents.text
    cur_list.append(company_name)

    # メインコンテンツを取得
    # 課題1 仕事内容、給与などを取得
    for main_content in company_element.find_elements_by_tag_name("tr"):
        try:
            cur_list.append(
                "{}:{}".format(
                    main_content.find_element_by_tag_name("th").text,
                    main_content.find_element_by_tag_name("td").text
                )
            )
        except:
            __write_log("{} 取得中にエラーが発生しました".format(main_content.text), ERROR)


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
