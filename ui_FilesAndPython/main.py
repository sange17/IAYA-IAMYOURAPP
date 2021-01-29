import sys
import time
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import quote_plus
from selenium import webdriver
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import urllib.request
from PyQt5.QtGui import QPixmap
from selenium.webdriver.common.keys import Keys

# 기본 Ui
ui = uic.loadUiType("./main.ui")[0]
uiMap = uic.loadUiType("./KonyangUniversityMap.ui")[0]
uiInfo = uic.loadUiType("./KonyangInfo.ui")[0]
uiCon = uic.loadUiType("./KonyangContract.ui")[0]

#COVID_19 코로나 구현
page = requests.get('http://ncov.mohw.go.kr/bdBoardList_Real.do?brdld=1&brdGubun=13&ncvContSeq=&contSeq=&board_id=&gubun=')
soup = BeautifulSoup(page.content, 'html.parser')

data = soup.find('div', class_='mapview')

data_text = data.find_all('span', class_='tit')
data_value = data.find_all('span', class_='num')
data_value_num = data.find_all('em')

data_sub_text = data.find('span', class_='sub_tit red')
data_sub_num = data.find('span', class_='sub_num red')

for i in range(len(data_text)):
    corona_today = data_sub_text.get_text() + data_sub_num.get_text()
    coronaA = data_text[0].get_text() + data_value[0].get_text() + data_value_num[0].get_text()
    coronaB = data_text[2].get_text() + data_value[2].get_text() + data_value_num[2].get_text()
    coronaC = data_text[1].get_text() + data_value[1].get_text() + data_value_num[1].get_text()
    coronaD = data_text[3].get_text() + data_value[3].get_text() + data_value_num[3].get_text()
corona = corona_today + '\n' + coronaA + '\n' + coronaB + '\n' + coronaC + '\n' + coronaD


# 영화 구현
page = requests.get('https://movie.naver.com/movie/running/current.nhn?view=image&tab=normal&order=reserve')
soup = BeautifulSoup(page.content, 'html.parser')

movie = soup.find('div', class_='lst_wrap')

movie_name = movie.find_all('strong', class_='tit') #영화제목
movie_num = movie.find_all('span', class_='dsc') # 영화별예매율
#movie_image = movie.find_all('img', onerror_='this.src') #영화이미지

movie_result = [0, 1, 2, 3, 4]

for i in range(len(movie_name)):
    if(i <= 4):
        movie_result[i] = movie_name[i].get_text() + '\n' + movie_num[i].get_text(": ")
    else:
        break

class WeatherBox:
    #url
    naver = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='
    google = 'https://www.google.com/search?q='
    #검색어
    keyword = quote_plus('내위치 날씨')
    #크롤링 멤버 1
    url = naver + keyword
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    #크롤링 멤버 2
    url2 = google + keyword
    page2 = requests.get(url2)
    soup2 = BeautifulSoup(page2.content, 'html.parser')

    # 온도 수치 구하기
    def WeatherValue(self):
        # 온도 값 가져오기
        soup = self.soup
        temperature = soup.select('div > p > span.todaytemp')
        return temperature[0].get_text()
    # celsius
    def WeatherCelsius(self):
        soup = self.soup
        tmp = soup.select('div > p > span.tempmark')
        s = tmp[0].get_text() #도씨℃
        tempmark = s[2:] #℃
        return tempmark
    # 맑음, 비, 흐림 등등
    def WeatherState(self):
        soup = self.soup
        state = soup.select_one('.cast_txt')
        s = str(state.get_text())
        pos = s.find(',') #비, 어제보다 1 낮아요 => 1값
        weather = s[0:pos] # s[0:1] => 비
        return weather
    # 강수확률 구하기
    def rainProb(self):
        browser = webdriver.Chrome('./chromedriver.exe')
        browser.get(self.url2) #구글 내위치 날씨 열기
        time.sleep(2)
        html = browser.page_source
        soup = BeautifulSoup(html)
        datas = soup.select('.wob-dtl > div')
        return datas[0].get_text()

class ITNews:
    url = 'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=105'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # 1. 뉴스 헤드라인 텍스트 가져오기
    def getHeadline(self, index):
        soup = self.soup
        # 헤드라인 앞, 뒤 크롤링
        headF = soup.select('div.cluster_head > div > div > h2 > a > span:nth-child(1)')
        headR = soup.select('div.cluster_head > div > div > h2 > a > span:nth-child(2)')

        headline = []
        li1 = []
        li2 = []

        # 헤드라인 앞부분 리스트 저장
        for data in headF:
            li1.append(data.get_text())

        # 헤드라인 뒷부분 리스트 저장
        for data in headR:
            li2.append(data.get_text())

        # 헤드라인 앞,뒤 묶음 리스트 저장
        for i in range(len(li1)):
            headline.append(li1[i] + li2[i])

        return headline[index]
    # 2. 뉴스 헤드라인 링크 가져오기
    def getHeadLink(self):
        soup = self.soup
        headlink = soup.select('div.cluster_head > div > div > h2 > a')
        results = []
        prefix = 'http://news.naver.com'
        for data in headlink:
            link = data.attrs['href']
            results.append(prefix + link)
        return results
    # 3. 각 헤드라인 첫 기사 링크 가져오기
    def getArticleLink(self):
        # 각 헤드라인의 첫번째 기사를 스크랩
        soup = self.soup
        titles = soup.select('ul.cluster_list')
        linklist = []
        # 기사 링크 가져오기
        for data in titles:
            link = data.a['href']
            linklist.append(link)

        return linklist
    # 4. 위 기사들의 이미지 링크주소 가져오기
    def getImageLinks(self, linklist):
        imgLinks = []
        # 링크 접속 후 사진 가져오기
        for i in range(len(linklist)):
            try:
                eachNewsUrl = linklist[i]
                eachNewspage = requests.get(eachNewsUrl)
                soup = BeautifulSoup(eachNewspage.content, 'html.parser')
                imglink = soup.select('span > img')
                imgsrc = imglink[0].attrs['src']
                imgLinks.append(imgsrc)
            #이미지 없는 기사 만났을 시 임의 이미지로 대체
            except:
                imgLinks.insert(i,'https://www.seekpng.com/png/full/423-4235598_no-image-for-noimage-icon.png')
        return imgLinks
    # 5. 링크 주소로 실제 이미지 가져오기
    def getArticleImage(self, index):  #imagelinks = getImageLinks
        targetImageLink = self.getImageLinks(self.getArticleLink())[index]
        # 웹 이미지 url을 읽어서 파일로 열기
        imageFromWeb = urllib.request.urlopen(targetImageLink).read()
        ArticleImage = QPixmap()
        ArticleImage.loadFromData(imageFromWeb)
        ArticleImage.scaledToHeight(160)

        return ArticleImage
    # 6. 기사의 제목 가져오기
    def getArticleTitle(self, linklist, index):
        eachNewsTitles = []
        # 링크에서 뉴스 제목 가져오기
        for i in range(len(linklist)):
            eachNewsUrl = linklist[i]
            eachNewspage = requests.get(eachNewsUrl)
            soup = BeautifulSoup(eachNewspage.content, 'html.parser')
            title = soup.select('h3')
            s = str(title[1].get_text())
            title = s[:30] + '\n' + s[30:] #줄바꿈문자 추가
            eachNewsTitles.append(title)

        return eachNewsTitles[index]
    # 7. 기사의 글 내용 가져오기
    def getArticleContents(self, linklist, index, MaxScrapSize):
        eachNewsContents = []
        for i in range(len(linklist)):
            eachNewsUrl = linklist[i]
            eachNewspage = requests.get(eachNewsUrl)
            soup = BeautifulSoup(eachNewspage.content, 'html.parser')
            article = soup.select('#articleBodyContents')

            s = str(article[0].get_text())
            content = s[5:MaxScrapSize] + '...' #앞 줄바꿈 문자 제거 + 끝 중략 삽입
            eachNewsContents.append(content)

        return eachNewsContents[index]


class MealTable:
    # 식단표 만들기
    def MakeMealTable(self):
        # 대전 식단표
        driver = webdriver.Chrome('./chromedriver.exe')
        driver.get('https://www.konyang.ac.kr/prog/sikdan/kor/sub06_06_03/list.do')
        time.sleep(3)

        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        meals = soup.find(class_='basic_table center')
        meals_date = meals.find_all('th')
        meals_meal = meals.find_all('td')

        list = [0,1,2,3,4]
        listMeals = []

        for i in range(5):
            list[i] = meals_date[i + 1].get_text() + '\n' + meals_meal[i + 7].get_text('\n') + '\n'
        meal_table1 = list[0] + '\n' + list[1] + '\n' + list[2] + '\n' + list[3] + '\n' + list[4]

        # 논산 식단표
        listMeals.append(meal_table1)
        # 논산 식단 크롤링 위한 옵션 변경
        sikdang = "//option[@value='" + '01' + "']"
        driver.find_element_by_xpath(sikdang).click()
        time.sleep(3)

        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        meals = soup.find(class_='basic_table center')
        meals_date = meals.find_all('th')
        meals_meal = meals.find_all('td')

        for i in range(5):
            list[i] = meals_date[i + 1].get_text() + '\n' + meals_meal[i + 7].get_text('\n') + '\n'
        meal_table2 = list[0] + '\n' + list[1] + '\n' + list[2] + '\n' + list[3] + '\n' + list[4]
        listMeals.append(meal_table2)
        driver.close()
        return listMeals

# 영화페이지 만들기 클래스
class MakeMoviePanel:
    browser = webdriver.Chrome('./chromedriver.exe')
    browser.implicitly_wait(30)
    url = 'https://movie.naver.com/movie/running/current.nhn?view=image&tab=normal&order=reserve'
    browser.get(url)
    block_imgs = browser.find_element_by_css_selector('div.top_poster_area')
    imgs = block_imgs.find_elements_by_css_selector('img')
    results = []

    for img in imgs:
        link = img.get_attribute('src')
        results.append(link)
    browser.close()
    #이미지 URL 가져오기
    def loadMovieImageLink(self):
        imagelinks = []
        for data in self.results:
            imagelinks.append(data)
        return imagelinks
    #이미지 가져오기
    def loadMovieImage(self, mvImageLinks, index):
        urlstring = mvImageLinks[index]
        imageFromWeb = urllib.request.urlopen(urlstring).read()
        qPixmapWebVar = QPixmap()
        qPixmapWebVar.loadFromData(imageFromWeb)
        qPixmapWebVar = qPixmapWebVar.scaledToWidth(200)

        return qPixmapWebVar

# 뉴스 객체 newsIt 생성
newsIt = ITNews()

# 식단, 영화 객체
mealT = MealTable(); myMovie = MakeMoviePanel()

class windows(QDialog,ui):
    # 날씨 클래스 객체 wb 생성
    wb = WeatherBox()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        #area open
        self.btn_Main_it_info.clicked.connect(self.itAreaOpen)
        self.btn_Main_movie_info.clicked.connect(self.MvAreaOpen)
        self.btn_Main_school_meal.clicked.connect(self.MealAreaOpen)
        self.btn_Main_konyang_info.clicked.connect(self.infoAreaOpen)

        #back btn
        self.btn_it_info_back.clicked.connect(self.Allclose)
        self.btn_Main_movie_info_back.clicked.connect(self.Allclose)
        self.btn_Main_school_meal_back.clicked.connect(self.Allclose)
        self.btn_info_back.clicked.connect(self.Allclose)

        #konyang info area
        self.btn_Konyang_Minimap_3.clicked.connect(self.MapOpen)
        self.btn_Konyang_info_3.clicked.connect(self.InfoOpen)
        self.btn_Konyang_Contract_3.clicked.connect(self.ConOpen)

        #All Area Close
        self.it_info_Area.setFixedSize(450, 0)
        self.movie_Area.setFixedSize(450, 0)
        self.school_meal_Area.setFixedSize(450, 0)
        self.info_Area.setFixedSize(450, 0)

        #movie area
        self.btn_Main_movie_info_next_1.clicked.connect(self.pageChangedNext)
        self.btn_Main_movie_info_next_2.clicked.connect(self.pageChangedNext)
        self.btn_Main_movie_info_next_3.clicked.connect(self.pageChangedNext)
        self.btn_Main_movie_info_next_4.clicked.connect(self.pageChangedNext)
        self.btn_Main_movie_info_next_5.clicked.connect(self.pageChangedNext)
        self.idx = 0
        self.btn_Main_movie_info_before_1.clicked.connect(self.pageChangedBefore)
        self.btn_Main_movie_info_before_2.clicked.connect(self.pageChangedBefore)
        self.btn_Main_movie_info_before_3.clicked.connect(self.pageChangedBefore)
        self.btn_Main_movie_info_before_4.clicked.connect(self.pageChangedBefore)
        self.btn_Main_movie_info_before_5.clicked.connect(self.pageChangedBefore)

        #corona, movie
        self.lbl_Main_corona.setText(corona)
        self.lbl_movie_name_1.setText(movie_result[0])
        self.lbl_movie_name_2.setText(movie_result[1])
        self.lbl_movie_name_3.setText(movie_result[2])
        self.lbl_movie_name_4.setText(movie_result[3])
        self.lbl_movie_name_5.setText(movie_result[4])

        # 영화
        movieImages = [self.lbl_movie_image_1, self.lbl_movie_image_2, self.lbl_movie_image_3, self.lbl_movie_image_4,
                       self.lbl_movie_image_5]
        for i in range(len(movieImages)):
            movieImages[i].setPixmap(myMovie.loadMovieImage(myMovie.loadMovieImageLink(), i))

        #날씨
        self.lbl_weather_weather.setText(self.wb.WeatherState())
        self.lbl_weather_temp.setText(self.wb.WeatherValue())
        self.lbl_weather_rainfall.setText(self.wb.rainProb())

        #뉴스
        newsimgs = [self.lbl_photo_1, self.lbl_photo_2, self.lbl_photo_3]
        newstitles = [self.lbl_contents_1_1, self.lbl_contents_2_1, self.lbl_contents_3_1]
        newscontents = [self.lbl_contents_1_2, self.lbl_contents_2_2, self.lbl_contents_3_2]
        for i in range(3):
            self.page_headline_3.setItemText(i, newsIt.getHeadline(i))
            newsimgs[i].setPixmap(newsIt.getArticleImage(i))  # 이미지 레이블 값 변경하기
            newstitles[i].setText(newsIt.getArticleTitle(newsIt.getArticleLink(), i))
            newscontents[i].setText(newsIt.getArticleContents(newsIt.getArticleLink(), i, 300))

        #식단
        Tables = []
        for data in mealT.MakeMealTable():
            Tables.append(data)
        self.lbl_school_meal_deajon.setText(Tables[0])
        self.lbl_school_meal_nonsan.setText(Tables[1])

    def pageChangedBefore(self):
        if(self.idx == 0 or self.idx == -1):
            self.idx = 4
        else:
            self.idx-= 1
        self.movie_Area_stack.setCurrentIndex(self.idx)


    def pageChangedNext(self):
        self.idx+=1
        if((self.idx//6) != 0):
            self.idx = 0
        self.movie_Area_stack.setCurrentIndex(self.idx)

    def itAreaOpen(self):
        self.it_info_Area.setFixedSize(450,630)
    def MvAreaOpen(self):
        self.movie_Area.setFixedSize(450, 630)
    def MealAreaOpen(self):
        self.school_meal_Area.setFixedSize(450, 630)


    def infoAreaOpen(self):
        self.info_Area.setFixedSize(450, 630)

    def Allclose(self):
        self.idx = 0 #영화 스텍패널 인덱스
        self.movie_Area_stack.setCurrentIndex(self.idx) #스텍패널 위치 초기화
        self.it_info_Area.setFixedSize(450, 0)
        self.movie_Area.setFixedSize(450, 0)
        self.school_meal_Area.setFixedSize(450, 0)
        self.info_Area.setFixedSize(450, 0)


    def MapOpen(self):
        Map_Area(self)
    def InfoOpen(self):
        Info_Area(self)
    def ConOpen(self):
        Con_Area(self)

class Map_Area(QDialog, uiMap):

    def __init__(self, parent):
        super(Map_Area, self).__init__(parent)
        self.setupUi(self)
        self.show()

        def loadImageFromWeb(self):
            urlstring = 'http://www.konyang.ac.kr/cyber/images/campus/medi_gyu.png'
            imageFromWeb = urllib.request.urlopen(urlstring).read()
            self.qPixmapWebVar = QPixmap()
            self.qPixmapWebVar.loadFromData(imageFromWeb)
            self.qPixmapWebVar = self.qPixmapWebVar.scaledToWidth(600)
            self.label_Minimap.setPixmap(self.qPixmapWebVar)

        loadImageFromWeb(self)
        self.btn_FindwayToKonyang.clicked.connect(self.FindwayToKonyang)
        self.btn_Minimap_close.clicked.connect(self.thisClose)

    def thisClose(self):
        self.close()

    def FindwayToKonyang(self):
        n = self.btn_CurrentLocation.text()
        browser = webdriver.Chrome("./chromedriver.exe")
        browser.get('https://www.google.com/maps/dir///@36.3272011,127.3727549,14z')
        time.sleep(1)

        search = browser.find_element_by_css_selector("#sb_ifc50 > input")
        search.send_keys(n)
        search.send_keys(Keys.ENTER)

        d ="건양대학교병원"
        search2 = browser.find_element_by_css_selector("#sb_ifc51 > input")
        search2.send_keys(d)
        search2.send_keys(Keys.ENTER)

class Info_Area(QDialog,uiInfo):
    def __init__(self,parent):
        super(Info_Area,self).__init__(parent)
        self.setupUi(self)
        self.show()

        ## 공지사항 페이지

        # 장학
        page = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000584/selectBoardList.do")
        soup = BeautifulSoup(page.content, "html.parser")

        lst = []
        hacdata2 = soup.select("td.left > div > span.link > a")
        for data in hacdata2:
            link = data['href']
            lst.append(link)
        lst2 = []
        hacdata3 = soup.select("td.left > div > span.link > a > b")
        for data in hacdata3:
            lst2.append(data.get_text())

        lbllst = [self.label_2,self.label_3,self.label_4,self.label_5,self.label_6,self.label_7,self.label_8,self.label_9,self.label_10,self.label_11]


        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)


        page2 = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000585/selectBoardList.do")
        soup2 = BeautifulSoup(page2.content, "html.parser")

        lbllst = [self.label_12, self.label_13, self.label_14, self.label_15, self.label_16, self.label_17, self.label_18,
                  self.label_19, self.label_20, self.label_21]
        lst = []
        jangdata2 = soup2.select("td.left > div > span.link > a")
        for data in jangdata2:
            link = data['href']
            lst.append(link)

        lst2 = []
        jangdata3 = soup2.select("td.left > div > span.link > a > b")
        for data in jangdata3:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)

        page3 = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000883/selectBoardList.do")
        soup3 = BeautifulSoup(page3.content, "html.parser")

        lbllst = [self.label_22, self.label_23, self.label_24, self.label_25, self.label_26, self.label_27,
                  self.label_28,  self.label_29, self.label_30,self.label_31]
        lst = []
        studentdata = soup3.select("td.left > div > span.link > a")
        for data in studentdata:
            link = data['href']
            lst.append(link)

        lst2 = []
        studentdata2 = soup3.select("td.left > div > span.link > a > b")
        for data in studentdata2:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)

        page4 = requests.get("https://job.konyang.ac.kr/cop/bbs/BBSMSTR_000000001381/selectBoardList.do")
        soup4 = BeautifulSoup(page4.content, "html.parser")

        lbllst = [self.label_32, self.label_33, self.label_34, self.label_35, self.label_36, self.label_37,
                  self.label_38, self.label_39, self.label_40, self.label_41]
        lst = []
        getjobdata = soup4.select("td.left > div > span.link > a")
        for data in getjobdata:
            link = data['href']
            lst.append(link)

        lst2 = []
        getjobdata2 = soup4.select("td.left > div > span.link > a")
        for data in getjobdata2:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://job.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)


        page5 = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000587/selectBoardList.do")
        soup5 = BeautifulSoup(page5.content, "html.parser")

        lbllst = [self.label_42, self.label_43, self.label_44, self.label_45, self.label_46, self.label_47,
                  self.label_48, self.label_49, self.label_50, self.label_51]

        lst = []
        applicationdata = soup5.select("td.left > div > span.link > a")
        for data in applicationdata:
            link = data['href']
            lst.append(link)

        lst2 = []
        applicationdata2 = soup5.select("td.left > div > span.link > a > b")
        for data in applicationdata2:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)


        page6 = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000588/selectBoardList.do")
        soup6 = BeautifulSoup(page6.content, "html.parser")

        lbllst = [self.label_52, self.label_53, self.label_54, self.label_55, self.label_56, self.label_57,
                  self.label_58, self.label_59, self.label_60, self.label_61]

        lst = []
        Hiredata = soup6.select("td.left > div > span.link > a")
        for data in Hiredata:
            link = data['href']
            lst.append(link)

        lst2 = []
        Hiredata2 = soup6.select("td.left > div > span.link > a > b")
        for data in Hiredata2:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)

        page7 = requests.get("https://www.konyang.ac.kr/cop/bbs/BBSMSTR_000000000583/selectBoardList.do")
        soup7 = BeautifulSoup(page7.content, "html.parser")

        lbllst = [self.label_62, self.label_63, self.label_64, self.label_65, self.label_66, self.label_67,
                  self.label_68, self.label_69, self.label_70, self.label_71]
        lst = []
        Nonmaldata = soup7.select("td.left > div > span.link > a")
        for data in Nonmaldata:
            link = data['href']
            lst.append(link)

        lst2 = []
        Nonmaldata2 = soup7.select("td.left > div > span.link > a > b")
        for data in Nonmaldata2:
            lst2.append(data.get_text())

        for i in range(len(lbllst)):
            lbllst[i].setOpenExternalLinks(True)
            lbllst[i].setText('<a href="https://www.konyang.ac.kr{0}">{1}</a>'.format(lst[i], lst2[i]))
            lbllst[i].linkActivated.connect(self.link)


        self.btn_Info_Close.clicked.connect(self.thisClose)

    def link(self,strlink):
        QDesktopServices.openUrl(QUrl(strlink))
        print(strlink)

    def thisClose(self):
        self.close()


class Con_Area(QDialog,uiCon):
    def __init__(self,parent):
        super(Con_Area,self).__init__(parent)
        self.setupUi(self)
        self.show()
        self.btn_Contract_Close.clicked.connect(self.thisClose)

        ### 의료공대 행정실 & 주요 민원부서 전화번호(의료공대 행정실, 교무팀, 장학팀, 기타)
        ## 의료공대 행정실 전화번호 모음
        # 의공학부
        page2 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_01_01.do')
        soup2 = BeautifulSoup(page2.content, 'html.parser')

        data2 = soup2.find(class_='content')
        data2_p = data2.find_all('p')
        data2_call = data2.find_all('a')

        BE = data2_p[0].get_text() + '  ' + data2_call[4].get_text()

        # 의료 IT 공학과
        page3 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_02_01.do')
        soup3 = BeautifulSoup(page3.content, 'html.parser')

        data3 = soup3.find(class_='content')
        data3_p = data3.find_all('p')
        data3_call = data3.find_all('a')

        MITE = data3_p[0].get_text() + '  ' + data3_call[4].get_text()

        # 의료 공간 디자인 학과
        page4 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_03_01.do')
        soup4 = BeautifulSoup(page4.content, 'html.parser')

        data4 = soup4.find(class_='content')
        data4_p = data4.find_all('p')
        data4_call = data4.find_all('a')

        DMSDM = data4_p[0].get_text() + '  ' + data4_call[4].get_text()

        # 의료 신소재 학과
        page5 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_04_01.do')
        soup5 = BeautifulSoup(page5.content, 'html.parser')

        data5 = soup5.find(class_='content')
        data5_p = data5.find_all('p')
        data5_call = data5.find_all('a')

        DBM = data5_p[0].get_text() + '  ' + data5_call[4].get_text()

        # 제약 생명 공학과
        page6 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_05_01.do')
        soup6 = BeautifulSoup(page6.content, 'html.parser')

        data6 = soup6.find(class_='content')
        data6_p = data6.find_all('p')
        data6_call = data6.find_all('a')

        DPB = data6_p[0].get_text() + '  ' + data6_call[4].get_text()

        # 의료 인공지능 학과
        page7 = requests.get('https://www.konyang.ac.kr/kor/sub03_05_07_01.do')
        soup7 = BeautifulSoup(page7.content, 'html.parser')

        data7 = soup7.find(class_='content')
        data7_p = data7.find_all('p')
        data7_call = data7.find_all('a')

        MAI = data7_p[0].get_text() + '  ' + data7_call[1].get_text()

        Contract = BE + '\n' + MITE + '\n' + DMSDM + '\n' + DBM + '\n' + DPB + '\n' + MAI
        self.textEdit_Contract1.setText(Contract)

        ## 주요 민원부서 전화번호

        # 교무팀 전화번호
        page = requests.get('https://www.konyang.ac.kr/kor/sub06_09_01.do')
        soup = BeautifulSoup(page.content, 'html.parser')

        data = soup.find(class_='tbl_basic')
        data_th = data.find_all('th')
        data_td = data.find_all('td')

        gyomu = data_th[3].get_text() + '\n' + data_td[0].get_text() + '\n' + data_td[1].get_text() \
                + '\n\n' + data_td[2].get_text().replace('\t', '') + '\n' + data_td[3].get_text()
        self.textEdit_Contract2.setText(gyomu)

        ## 장학팀 전화번호
        janghak = data_th[5].get_text() + '\n' + data_td[8].get_text() + '\n' + data_td[9].get_text()
        self.textEdit_Contract3.setText(janghak)

        # 학생지원팀
        jiwon = data_th[4].get_text() + '\n' + data_td[10].get_text() + '\n' + data_td[11].get_text()
        self.textEdit_Contract4.setText(jiwon)

        # 인성관
        insung = data_th[20].get_text() + '\n' + data_td[38].get_text() + '\n' + data_td[39].get_text()
        self.textEdit_Contract5.setText(insung)

    def thisClose(self):
            self.close()

app = QApplication(sys.argv)
w1 = windows()
w1.show()
app.exec()