import os
import random
import time
import json
import urllib.parse
import requests
import urllib
from lxml import etree
from ddddocr import DdddOcr
from config.config import Config
from Encrypt import encryptAES


class YSUinfo:
    URL_SERVICE = urllib.parse.quote("https://jwxt.ysu.edu.cn/jwmobile/index")
    URL_SERVICE_GPA = urllib.parse.quote(
        "https://jwxt.ysu.edu.cn/jwapp/sys/cjcx/*default/index.do?THEME=indigo&EMAP_LANG=zh#/cjcx?THEME=indigo&EMAP_LANG=zh"
    )
    URL_LOGIN = f"https://cer.ysu.edu.cn/authserver/login?service={URL_SERVICE}"
    URL_TEST = "https://jwxt.ysu.edu.cn/jwmobile/biz/v410/score/termScore"
    URL_LOGIN_SESSION = "https://jwxt.ysu.edu.cn/jwmobile/login/login.do"
    URL_AUTHORIZATION = "https://jwxt.ysu.edu.cn/jwmobile/auth/index"
    URL_TERMSCORE = "https://jwxt.ysu.edu.cn/jwmobile/biz/v410/score/termScore"
    URL_SCOREDETAIL = "https://jwxt.ysu.edu.cn/jwmobile/biz/v410/score/scoreDetail"
    URL_RECENTEXAMS = "https://jwxt.ysu.edu.cn/jwmobile/biz/v410/examTask/recentExams"
    URL_QUERYSCHEDULE = (
        "https://jwxt.ysu.edu.cn/jwmobile/biz/v410/schedule/querySchedule"
    )
    URL_WEEKS = "https://jwxt.ysu.edu.cn/jwmobile/biz/home/queryWelcomeContent"

    URL_GPA = "https://jwxt.ysu.edu.cn/jwapp/sys/cjcx/modules/cjcx/cxzxfaxfjd.do"

    URL_SCORE = "https://jwxt.ysu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do"

    def __init__(self, userName, passWord, useCache=True, loginType=0):
        """
        初始化

        :param username: 用户名
        :param password: 密码
        :param useCache: 是否使用缓存cookie
        :param type: 0为登录手机端,1为登录PC端(jwxt.ysu.edu.cn)
        """
        self.username = userName
        self.password = passWord
        self.useCache = useCache
        self.loginType = loginType
        self.session = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.session.headers.update(self.headers)
        self.cookies = None
        self.authorization = None
        self.set_login_url()
        self.load_session()

    def set_login_url(self):
        if self.loginType == 0:
            self.URL_LOGIN = (
                f"https://cer.ysu.edu.cn/authserver/login?service={self.URL_SERVICE}"
            )
        elif self.loginType == 1:
            self.URL_LOGIN = f"https://cer.ysu.edu.cn/authserver/login?service={self.URL_SERVICE_GPA}"

    def pushMessage(self, token, title, message):
        url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={message}&template=html"
        requests.get(url).json()

    def load_session(self):
        if self.useCache and self.loginType == 0:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                session_path = os.path.join(current_dir, "./config/session.json")
                with open(session_path, "r") as f:
                    session_data = json.load(f)
                self.session.cookies.update(session_data)
                self.authorization = session_data["Authorization"]
                self.cookies = session_data
            except FileNotFoundError:
                print("未找到session文件,正在重新登录获取..")
                self.refresh_session()
        else:
            self.refresh_session()

    def refresh_session(self):
        self.login()
        self.save_session()

    def save_session(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        session_path = os.path.join(current_dir, "./config/session.json")
        with open(session_path, "w") as f:
            json.dump(self.session.cookies.get_dict(), f)

    def login(self):
        """
        Login into YSU CAS

        :return: session that contains cookies
        """
        lt_v, dllt_v, execution_v, event_id_v, pwdSalt = self._get_login_parameters(
            self.session
        )
        pwdEcy = self._encrypt_password(pwdSalt)

        workload = {
            "username": self.username,
            "password": pwdEcy,
            "rememberMe": "true",
            "lt": lt_v,
            "dllt": dllt_v,
            "execution": execution_v,
            "_eventId": event_id_v,
            "captcha": "",
        }

        if self._needs_captcha(self.session, self.username):
            code = self._get_captcha(self.session)
            workload["captcha"] = code

        result = self.session.post(self.URL_LOGIN, data=workload, allow_redirects=False)

        if "happyVoyage" in self.session.cookies:
            location = result.headers.get("Location")
            loc = self._get_MOD_AUTH_CAS(location)
            if self.loginType == 1:
                # 需要多次请求才能获取到最终236位的_WEU参数
                self._get_WUE_new_1()
                self._get_WUE_new_2()
                self._get_WUE_new_3()

            else:
                Authorization = self._get_Authorization()
                self.authorization = Authorization
            self.cookies = self.session.cookies.get_dict()
            return self.session
        else:
            print("Login failed, waiting for 5 seconds...")
            time.sleep(3)
            self.login()

    # 新版 1-3
    def _get_WUE_new_1(self):
        locationUrl = "https://jwxt.ysu.edu.cn/jwapp/sys/funauthapp/api/getAppConfig/cjcx-4768574631264620.do?v=0649627056680742"
        res = self.session.get(locationUrl, allow_redirects=False, headers=self.headers)

    def _get_WUE_new_2(self):
        locationUrl = (
            "https://jwxt.ysu.edu.cn/jwapp/sys/jwpubapp/modules/bb/cxjwggbbdqx.do"
        )
        data = {"APP": "4768574631264620", "SFQY": "1"}
        res = self.session.post(
            locationUrl, allow_redirects=False, headers=self.headers, data=data
        )

    def _get_WUE_new_3(self):
        locationUrl = "https://jwxt.ysu.edu.cn/jwapp/sys/emappagelog/config/cjcx.do"
        res = self.session.get(locationUrl, allow_redirects=False, headers=self.headers)

    # 旧版 1-6
    def _get_WEU_1(self, locationUrl):
        res = self.session.get(locationUrl, allow_redirects=False, headers=self.headers)
        location = res.headers.get("Location")
        return location

    def _get_WEU_2(self, locationUrl):
        res = self.session.get(locationUrl, allow_redirects=False, headers=self.headers)
        print("_get_WEU_2", res.text)
        appid = res.text.split('"appId":"')[1].split('","_v"')[0]
        return appid

    def _get_WEU_3(self, appid):
        url = "https://jwxt.ysu.edu.cn/jwapp/sys/jwpubapp/modules/bb/cxjwggbbdqx.do"
        data = {"APP": appid, "SFQY": "1"}
        self.session.post(url, data=data, headers=self.headers)

    def _get_WEU_4(self, appid):
        url = f"https://jwxt.ysu.edu.cn/jwapp/sys/funauthapp/api/getAppConfig/cjcx-{appid}.do?v=03089445764325194"
        self.session.get(url, headers=self.headers)

    def _get_WEU_5(self):
        url = "https://jwxt.ysu.edu.cn/jwapp/sys/homeapp/index.do"
        self.session.get(url, headers=self.headers)

    def _get_WEU_6(self):
        url = "https://jwxt.ysu.edu.cn/jwapp/sys/emappagelog/config/cjcx.do"
        self.session.get(url, headers=self.headers)

    def _get_MOD_AUTH_CAS(self, locationUrl):
        res = self.session.get(locationUrl, allow_redirects=False)
        location = res.headers.get("Location")
        return location

    def _get_Authorization(self):
        url = self.URL_AUTHORIZATION
        res = self.session.get(url, allow_redirects=False)
        location = res.headers["Location"]
        Authorization = location.split("token=")[1]
        self.session.cookies.set("Authorization", Authorization)
        return Authorization

    def _get_login_parameters(self, session):
        result = session.get(self.URL_LOGIN)
        result.raise_for_status()  # Raise exception for non-200 response
        tree = etree.HTML(result.text)

        lt_v = tree.xpath('//input[@name="lt"]/@value')[0]
        dllt_v = tree.xpath('//input[@name="dllt"]/@value')[0]
        execution_v = tree.xpath('//input[@name="execution"]/@value')[0]
        event_id_v = tree.xpath('//input[@name="_eventId"]/@value')[0]
        pwdSalt = tree.xpath('//*[@id="pwdEncryptSalt"]/@value')[0]

        return lt_v, dllt_v, execution_v, event_id_v, pwdSalt

    def _encrypt_password(self, pwdSalt):
        if not self.username or not self.password:
            exit(2)

        return encryptAES(self.password, pwdSalt)

    def _needs_captcha(self, session, username):
        capt_result = session.get(
            f"https://cer.ysu.edu.cn/authserver/needCaptcha.html?username={username}&pwdEncrypt2=pwdEncryptSalt&_={int(time.time())}"
        )
        return "true" in capt_result.text

    def _get_captcha(self, session):
        captimg_result = session.get(
            f"https://cer.ysu.edu.cn/authserver/getCaptcha.htl?ts={random.randint(1, 999)}"
        )
        ocr = DdddOcr(show_ad=False)
        return ocr.classification(captimg_result.content)

    def _get_weeks(self):
        url = self.URL_WEEKS
        response = self.session.post(url, headers=self.headers)
        obj = response.json()
        return obj["data"]["dateTipText"].split("现在是第")[1].split("周")[0]

    def get_term_score(self):
        url = self.URL_TERMSCORE
        payload = {"termCode": "2024-2025-1", "courseNature": "", "courseName": ""}
        response = self.session.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_score_detail(self, id):
        """
        :param id: 课程id
        """
        url = self.URL_SCOREDETAIL
        payload = {"id": f"{id}"}
        response = self.session.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_recentExams(self):
        url = self.URL_RECENTEXAMS
        payload = {"termCode": "2024-2025-1", "courseNature": "", "courseName": ""}
        response = self.session.get(url, json=payload, headers=self.headers)
        return response.json()

    def get_querySchedule(self):
        url = self.URL_QUERYSCHEDULE
        playload = {"skzc": self._get_weeks(), "xnxqdm": "2024-2025-1"}
        response = self.session.post(url, json=playload, headers=self.headers)
        return response.json()

    def get_gpa(self, username):
        url = self.URL_GPA
        data = {
            "XH1": username,
            "XH2": username,
            "XH3": username,
            "XH4": username,
            "XH5": username,
            "XH6": username,
        }
        response = self.session.post(url, data=data, headers=self.headers)
        return response.json()

    def get_score_list(self):
        url = self.URL_SCORE
        data = {
            "querySetting": '[{"name":"SFYX","caption":"是否有效","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"1","value_display":"是"},{"name":"SHOWMAXCJ","caption":"显示最高成绩","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"0","value_display":"否"},{"name":"BY1","caption":"备用1","linkOpt":"AND","builderList":"cbl_m_List","builder":"equal","value":"1"}]',
            "order": "-XNXQDM,-KCH,-KXH",
            "pageSize": "100",
            "pageNumber": "1",
        }
        response = self.session.post(url, data=data, headers=self.headers)
        return response.json()


def calculateGPA(grades, credits, is_degree_course, degree_multiplier=1.2):
    """
    计算加权平均学分绩点（GPA）教务处给出计算公式:
    加权平均学分绩点 = ∑[(非学位课绩点×非学位课课程学分)+(学位课绩点×学位课课程学分)*1.2] / ∑[非学位课课程学分+学位课课程学分*1.2]

    :param grades: 一个列表，包含课程的绩点。
    :param credits: 一个列表，包含对应课程的学分。
    :param is_degree_course: 一个布尔值列表，True表示学位课程，False表示非学位课程。
    :param degree_multiplier: 学位课程的权重倍数，默认为1.2。
    :return: 加权平均学分绩点。
    """
    # 检查输入列表长度是否一致
    if len(grades) != len(credits) or len(grades) != len(is_degree_course):
        raise ValueError("绩点列表、学分列表和课程类型列表的长度必须相同。")

    # 初始化分子和分母的和
    numerator = 0
    denominator = 0

    # 遍历绩点、学分和课程类型列表，计算加权和
    for grade, credit, is_degree in zip(grades, credits, is_degree_course):
        if grade < 0 or credit < 0:
            raise ValueError("绩点和学分不能为负数。")
        # 非学位课程
        if not is_degree:
            numerator += grade * credit
            denominator += credit
        # 学位课程，乘以权重倍数
        else:
            numerator += grade * credit * degree_multiplier
            denominator += credit * degree_multiplier

    # 计算加权平均学分绩点
    if denominator == 0:
        raise ValueError("学分总和不能为零。")
    weighted_gpa = numerator / denominator

    return weighted_gpa


def pushScore():
    cfg = Config()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    score_path = os.path.join(current_dir, "./config/score.json")
    try:
        ysuinfo = YSUinfo(cfg.username, cfg.password)
        scoreJson = ysuinfo.get_term_score()
        newScoreJson = scoreJson["data"]["termScoreList"][0]["scoreList"]
    except Exception as e:
        print(f"Error: {e}. Attempting to re-login.")
        ysuinfo = YSUinfo(cfg.username, cfg.password, False)
        scoreJson = ysuinfo.get_term_score()
        newScoreJson = scoreJson["data"]["termScoreList"][0]["scoreList"]
    try:
        with open(score_path, "r", encoding="utf-8") as f:
            fileJson = json.load(f)
    except:
        fileJson = newScoreJson
        with open(score_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(fileJson))

    msg = ""
    for score in newScoreJson:
        if score not in fileJson:
            print("出分了！")
            msg = (
                (
                    "课程:"
                    + score["courseName"]
                    + "  成绩:"
                    + score["score"]
                    + "   学分:"
                    + score["coursePoint"]
                    + "\n"
                )
                .replace("+", "加")
                .replace("-", "减")
            )
    if msg != "":
        with open(score_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(newScoreJson))
        print(msg)
        ysuinfo.pushMessage(cfg.pushkey, "出分了！", msg)
    else:
        print("未出分")


def pushGPA_online():
    cfg = Config()
    try:
        ysuinfo = YSUinfo(cfg.username, cfg.password, True, 1)
        gpaJson = ysuinfo.get_gpa(cfg.username)
    except Exception as e:
        print(f"Error: {e}. Attempting to re-login.")
        ysuinfo = YSUinfo(cfg.username, cfg.password, False, 1)
        gpaJson = ysuinfo.get_gpa(cfg.username)
    print(gpaJson)


def pushGPA_offline():
    cfg = Config()
    try:
        ysuinfo = YSUinfo(cfg.username, cfg.password, True, 1)
        gpaJson = ysuinfo.get_score_list()
    except Exception as e:
        print(f"Error: {e}. Attempting to re-login.")
        ysuinfo = YSUinfo(cfg.username, cfg.password, False, 1)
        gpaJson = ysuinfo.get_score_list()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scoreList_path = os.path.join(current_dir, "./config/scoreList.json")
    with open(scoreList_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(gpaJson))
    fileJson = gpaJson
    loopint = fileJson["datas"]["xscjcx"]["totalSize"]
    score_grades = []
    score_credits = []
    score_degree = []
    print("课程数量 -> ", loopint)
    for i in range(loopint):
        # 绩点
        XFJD = fileJson["datas"]["xscjcx"]["rows"][i]["XFJD"]
        # 总成绩
        ZCJ = fileJson["datas"]["xscjcx"]["rows"][i]["ZCJ"]
        # 课程名称
        XSKCM = fileJson["datas"]["xscjcx"]["rows"][i]["XSKCM"]
        # 学分
        XF = fileJson["datas"]["xscjcx"]["rows"][i]["XF"]
        # 考核方式
        CXCKDM_DISPLAY = fileJson["datas"]["xscjcx"]["rows"][i]["CXCKDM_DISPLAY"]
        # 是否学位课
        SFZGKC_DISPLAY = fileJson["datas"]["xscjcx"]["rows"][i]["SFZGKC_DISPLAY"]

        if CXCKDM_DISPLAY == "正考":
            # print(XFJD, ZCJ, XSKCM, XF)
            score_grades.append(float(XFJD))
            score_credits.append(float(XF))
            if SFZGKC_DISPLAY == "是":
                score_degree.append(True)
            else:
                score_degree.append(False)
    # 计算GPA
    gpa = calculateGPA(score_grades, score_credits, score_degree)
    print(f"加权平均学分绩点（GPA）: {gpa:.3f}")
    msg = f"加权平均学分绩点（GPA）: {gpa:.3f}"
    return msg
    # ysuinfo.pushMessage(cfg.pushkey, "绩点查询结果", msg)


if __name__ == "__main__":
    pushScore()
    pushGPA_online()
    pushGPA_offline()
