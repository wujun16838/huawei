# -*- coding: utf-8 -*-
# !/usr/bin/python
import time

from selenium import webdriver
from datetime import datetime

from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from configparser import ConfigParser


class HuaWei:
    browser = None
    configparser = None
    isLogin = False
    isCountdown = True
    isStartBuying = False
    isBuying = False
    nickname = "游客"
    # 全局页面元素超时时间，单位S
    defaultTimeout = 60

    def __init__(self, config_file):
        self.__config_parse(config_file)
        self.__browser_setting()

    def start_process(self):
        print("{0} 开启抢购华为 {1} 手机".format(datetime.now(), self.__config_get("product", "name")))
        self.__visit_official_website()
        self.__login()
        if self.isLogin:
            self.__visit_product_page()
            self.__choose_product()
            self.__countdown()

    def stop_process(self):
        print("{0} 结束抢购华为 {1} 手机".format(datetime.now(), self.__config_get("product", "name")))
        time.sleep(5)
        self.browser.quit()

    def __visit_official_website(self):
        print("{0} 开始进入华为官网".format(datetime.now()))
        self.browser.get('https://www.vmall.com/')
        print("{0} 已进入华为官网".format(datetime.now()))

    def __visit_product_page(self):
        print("{0} 开始进入华为 {1} 产品详情页".format(datetime.now(), self.__config_get("product", "name")))
        self.browser.get("https://www.vmall.com/product/{0}.html".format(self.__config_get("product", "id")))
        self.browser.refresh()
        self.browser.implicitly_wait(20)
        print("{0} 已进入华为 {1} 产品详情页".format(datetime.now(), self.__config_get("product", "name")))

    def __choose_product(self):
        print("{0} 开始选择手机规格".format(datetime.now()))
        sku_color = self.__config_get("product", "color")
        sku_version = self.__config_get("product", "version")
        sku_payment = self.__config_get("product", "payment")
        WebDriverWait(self.browser, self.defaultTimeout).until(
            EC.presence_of_element_located((By.LINK_TEXT, f"{sku_color}"))
        ).click()
        WebDriverWait(self.browser, self.defaultTimeout).until(
            EC.presence_of_element_located((By.LINK_TEXT, f"{sku_version}"))
        ).click()
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, f"{sku_payment}"))
        ).click()
        print("{0} 选择手机规格完成，颜色：{1} 版本：{2} 付款方式：{3}".format(datetime.now(), sku_color, sku_version, sku_payment))
        time.sleep(0.01)

    def __login(self):
        print("{0} 开始登陆华为账号".format(datetime.now()))
        self.__goto_login_page()
        self.__submit_login()
        self.__check_is_login()

        """ 
        TODO：实现cookie记录，并实现Cookie登陆
        """
        if self.isLogin:
            print("{0} 当前登陆账号为：{1}".format(datetime.now(), self.nickname))

        print("{0} 结束登陆华为账号".format(datetime.now()))

    def __browser_setting(self):
        print("{0} 开始设置浏览器参数".format(datetime.now()))
        options = webdriver.ChromeOptions()
        service = Service(executable_path=r'D:\git\hw_seckill\chromedriver.exe')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.add_argument(r"--user-data-dir={}".format(self.__config_get("chrome", "userDataDir")))
        # options.add_argument(r"--profile-directory={}".format("Profile 5"))
        options.add_argument('--ignore-certificate-errors')
        browser = webdriver.Chrome(service=service, options=options)
        print("{0} 设置浏览器参数完成".format(datetime.now()))
        browser.maximize_window()
        self.browser = browser

    def __countdown(self):
        while self.isCountdown:
            countdown_times = self.__get_countdown_time()
            print("{0} 距离抢购开始还剩：{1}".format(datetime.now(), self.__format_countdown_time(countdown_times)))
            self.__set_start_buying(countdown_times)
            if not self.isStartBuying:
                time.sleep(1)
            else:
                self.__start_buying()

    def __start_buying(self):
        while self.isStartBuying:
            countdown_times = self.__get_countdown_time()
            if(not self.isBuying):
                print("{0} 距离抢购开始还剩：{1}".format(datetime.now(), self.__format_countdown_time(countdown_times)))
                self.browser.refresh()
                self.browser.implicitly_wait(20)
                self.__choose_product()
                self.browser.implicitly_wait(100)
                button_element = WebDriverWait(self.browser, self.defaultTimeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='pro-operation']/a"))
                )
            if(button_element.text != '暂时缺货'):
                button_element.click()
                print("刷到手机开始抢购")
                self.isBuying = True
            time.sleep(0.0001)
            self.__set_start_buying(countdown_times)
        self.__countdown()
        

    def __get_countdown_time(self):
        attempts = 0
        current_time = datetime.now()
        countdown_times = ["00","00","00","60"]
        minute = current_time.minute
        if(minute == 1 or minute == 3 or minute == 5 or minute == 7 or minute == 9
           or minute == 11 or minute == 13 or minute == 15 or minute == 17 or minute == 19
           or minute == 21 or minute == 23 or minute == 25 or minute == 27 or minute == 29
           or minute == 31 or minute == 33 or minute == 35 or minute == 37 or minute == 39
           or minute == 41 or minute == 43 or minute == 45 or minute == 47 or minute == 49
           or minute == 51 or minute == 53 or minute == 55 or minute == 57 or minute == 59):
            countdown_times[3] = "0"
        else:
            countdown_times[3] = str(60 - current_time.second)
        # while attempts < 5:
        #     try:
        #         elements = WebDriverWait(self.browser, self.defaultTimeout).until(
        #             EC.presence_of_all_elements_located((By.XPATH, "//div[@id='pro-operation-countdown']/ul/li/span"))
        #         )
        #         for element in elements:
        #             countdown_times.append(element.text)
        #         return countdown_times
        #     except (StaleElementReferenceException, TimeoutException):
        #         # 页面元素因为动态渲染，导致查找的元素不再是原来的元素，导致异常
        #         self.browser.refresh()
        #         self.browser.implicitly_wait(20)
        #         self.__choose_product()
        #         attempts += 1
        return countdown_times

    def __config_get(self, group_name, item_name):
        return self.configparser.get(group_name, item_name)

    def __config_parse(self, config_file):
        print("{0} 开始解析配置文件".format(datetime.now()))
        configparser = ConfigParser()
        configparser.read(config_file, "utf-8")
        self.configparser = configparser
        print("{0} 结束解析配置文件".format(datetime.now()))
        time.sleep(0.01)

    @staticmethod
    def __format_countdown_time(countdown_times):
        countdown_all_times = []
        countdown_time_units = ["天", "时", "分", "秒"]
        for index, countdown_time in enumerate(countdown_times):
            countdown_all_times.append(countdown_time)
            countdown_all_times.append(countdown_time_units[index])
        return " ".join(countdown_all_times)

    def __set_start_buying(self, countdown_times):
        if countdown_times[0] != "00" or countdown_times[1] != "00" or countdown_times[2] != "00":
            return
        if int(countdown_times[3]) < 10:
            self.isCountdown = False
            self.isStartBuying = True
        else:
            self.isCountdown = True
            self.isStartBuying = False

    def __goto_login_page(self):
        print("{0} 点击登录按钮".format(datetime.now()))
        login = WebDriverWait(self.browser, self.defaultTimeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "r-1a7l8x0"))
        )
        login.click()
        print("{0} 已跳转登录页面".format(datetime.now()))

    def __submit_login(self):
        """
        TODO：首次登陆浏览器不可信需要验证码登陆
        """
        print("{0} 开始输入账号及密码".format(datetime.now()))
        input_elements = WebDriverWait(self.browser, self.defaultTimeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "hwid-input"))
        )

        input_elements[0].send_keys(self.__config_get("user", "name"))
        input_elements[1].send_keys(self.__config_get("user", "password"))
        print("{0} 已输入账号及密码".format(datetime.now()))

        WebDriverWait(self.browser, self.defaultTimeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hwid-login-btn"))
        ).click()
        print("{0} 发起登陆请求".format(datetime.now()))
        self.browser.implicitly_wait(20)

    def __check_is_login(self):
        try:
            self.browser.find_element(By.LINK_TEXT, "请登录")
            self.isLogin = False
            print("{0} 账号登陆失败，请重试".format(datetime.now()))
        except NoSuchElementException:
            self.isLogin = True
            print("{0} 账号登陆成功".format(datetime.now()))
            self.nickname = WebDriverWait(self.browser, self.defaultTimeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "r-1pn2ns4"))
            ).text


