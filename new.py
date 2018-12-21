from slacker import Slacker
import websocket
import json
import urllib.request
from bs4 import BeautifulSoup



def run():
    slack = Slacker('xoxb-504131970294-507333492948-gfbVEOhHXoalXevCPgoTwwoO')

    response = slack.rtm.start()
    sock_endpoint = response.body['url']
    slack_socket = websocket.create_connection(sock_endpoint)
    slack_socket.settimeout(60)

    while True:
        try:
            msg = json.loads(slack_socket.recv())
            print(msg)

            if msg['type'] == 'message' and msg['user'] != "UEX9TEGTW":

                url = "https://movie.naver.com/movie/running/current.nhn"

                sourcecode = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(sourcecode, "html.parser")

                all_movies = []

                try:
                    for datas in soup.find_all("ul", class_="lst_detail_t1"):
                        for data in datas.find_all("li"):
                            if float(data.find("div", class_="b_star").find("span", class_="num").get_text()) > 0.9:
                                temp_dict = dict()

                                # 영화 이름 및 링크
                                temp_dict['name_src'] = url + data.find("dt", class_="tit").find("a").get('href')
                                temp_dict['name'] = data.find("dt", class_="tit").find("a").get_text()

                                # 영화 이미지 링크
                                temp_dict['img_src'] = data.find("div", class_="thumb").find("img").get("src")

                                # 평점 및 예매율
                                temp_dict['star'] = data.find("dl", class_="info_star").find("span",
                                                                                             class_='num').get_text()
                                array = data.find("dl", class_="info_exp").get_text().split()
                                temp_dict[array[0]] = array[1]

                                # 감독 및 출연배우
                                temp_dict['director'] = data.find("dl", class_="info_txt1").find_all("dd")[
                                    1].get_text().replace("\r", "").replace("\t", "").replace("\n", "")
                                temp_dict['actors'] = data.find("dl", class_="info_txt1").find_all("dd")[
                                    2].get_text().replace("\r", "").replace("\t", "").replace("\n", "")

                                # 예매 및 예고편 링크
                                temp_dict['reserve_link'] = url + data.find("a", class_="btn_rsv").get("href")
                                temp_dict['trailer_link'] = url + data.find("a", class_="item2").get("href")

                                all_movies.append(temp_dict)


                    if '현재' and '영화' in msg['text']:
                        if '평점순' in msg['text']:
                            all_movies.sort(key=lambda dic: float(dic['star']), reverse=True)

                        for movie in all_movies:
                            attachments_dict = dict()
                            attachments_dict['pretext'] = movie['name']
                            attachments_dict['title'] = movie['name']
                            attachments_dict['title_link'] = movie['name_src']
                            attachments_dict['text'] = '평점 : ' + movie['star'] + ', ' + '예매율 : ' + movie[
                                '예매율'] + '\n감독 : ' + movie['director'] + '\n출연배우 : ' + movie['actors'] + '\n'
                            attachments_dict['image_url'] = movie['img_src']
                            attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                            attachments_dict['actions'] = [
                                {
                                    "text": " 예매하기",
                                    "type": "button",
                                    "style": "danger",
                                    "url": movie['reserve_link']
                                },
                                {
                                    "text": "예고편",
                                    "type": "button",
                                    "style": "primary",
                                    "url": movie['trailer_link']
                                }
                            ]
                            attachments = [attachments_dict]
                            slack.chat.post_message(channel=msg['channel'], text=None, attachments=attachments,
                                                    as_user=True)

                    elif '줄거리' in msg['text']:
                        for movie in all_movies:
                            if movie['name'] in msg['text']:
                                url = movie['name_src']

                                sourcecode = urllib.request.urlopen(url).read()
                                soup = BeautifulSoup(sourcecode, "html.parser")

                                attachments_dict = dict()
                                attachments_dict['pretext'] = movie['name']
                                attachments_dict['title'] = '줄거리'
                                attachments_dict['text'] = soup.find_all("p", class_="con_tx")[0].get_text().replace('\xa0', ' ')
                                attachments = [attachments_dict]
                                slack.chat.post_message(channel=msg['channel'], text=None, attachments=attachments,
                                                        as_user=True)

                    # else:
                    #     slack.chat.post_message(channel=msg['channel'], text="키워드\n1. 현재 영화\n\t1-1.평점순, 예매율순(default)\n2. 줄거리 (영화 이름)")

                except:
                    pass

        except websocket.WebSocketTimeoutException:
            slack_socket.send(json.dumps({'type': 'ping'}))

        except websocket.WebSocketConnectionClosedException:
            print("Connection closed")
            break

        except Exception as e:
            print(e)
            break

    slack_socket.close()

while True:
    run()