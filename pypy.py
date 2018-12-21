import urllib.request
from bs4 import BeautifulSoup

url = "https://movie.naver.com/movie/running/current.nhn"
req = urllib.request.Request(url)

sourcecode = urllib.request.urlopen(url).read()
soup = BeautifulSoup(sourcecode, "html.parser")

all_movies = []

try:
    for datas in soup.find_all("ul", class_="lst_detail_t1"):
        i = 1
        for data in datas.find_all("li"):
            if float(data.find("div", class_="b_star").find("span", class_="num").get_text()) > 0.9:
                temp_dict = dict()

                #영화 이름 및 링크
                temp_dict['name_src'] = url + data.find("dt", class_="tit").find("a").get('href')
                temp_dict['name'] = data.find("dt", class_="tit").find("a").get_text()

                #사진 추출
                temp_dict['pic_num'] = str(i)
                urllib.request.urlretrieve(data.find("div", class_="thumb").find("img").get("src"), "./img/" + temp_dict['pic_num'] + ".jpg")

                #평점 및 예매율
                temp_dict['star'] = data.find("dl", class_="info_star").find("span", class_='num').get_text()
                array = data.find("dl", class_="info_exp").get_text().split()
                temp_dict[array[0]] = array[1]

                #감독 및 출연배우
                temp_dict['director'] = data.find("dl", class_="info_txt1").find_all("dd")[1].get_text().replace("\r", "").replace("\t", "").replace("\n", "")
                temp_dict['actors'] = data.find("dl", class_="info_txt1").find_all("dd")[2].get_text().replace("\r", "").replace("\t", "").replace("\n", "")

                #예매 및 예고편 링크
                temp_dict['reserve_link'] = url + data.find("a", class_="btn_rsv").get("href")
                temp_dict['trailer_link'] = url + data.find("a", class_="item2").get("href")

                print(temp_dict)
                i += 1
except:
    pass