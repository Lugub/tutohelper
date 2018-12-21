# -*- coding: utf-8 -*-
import json
import os
import random
import re
import urllib.request
from string import punctuation
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template


app = Flask(__name__)

slack_token = "xoxb-503773686820-507488178082-wj8zy7wTJNWJqLW4KBICLZOk"
slack_client_id = "503773686820.508539712295"
slack_client_secret = "b774252d8d6bd08825c4ec00c278c287"
slack_verification = "cSQtS76M7c6tmM81m0Fa0njo"
sc = SlackClient(slack_token)


#=====================================================================================
#                               초기에 크롤링 & 데이터 쌓기
#=====================================================================================
url = "https://us.soccerway.com/national/england/premier-league/20182019/regular-season/r48730/?ICID=SN_01_01"
soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

urls = []       #각 구단 페이지들의 url들이 들어감
teams = []      #전체적인 정보에 앞서 한번 거른 내용들이 들어감
teams_dic = {}  #전체적인 정보가 들어감
team_name_en = ['AFC Bournemouth', 'Arsenal', 'Brighton & Hov…', 'Burnley', 'Cardiff City', 'Chelsea',
             'Crystal Palace', 'Everton', 'Fulham', 'Huddersfield Town', 'Leicester City', 'Liverpool',
             'Manchester City', 'Manchester United', 'Newcastle United', 'Southampton', 'Tottenham Hotspur',
             'Watford', 'West Ham United', 'Wolverhampton …']

team_name_kr = {'본머스': 0,'AFC Bournemouth':0 ,'Liverpool':11,'Arsenal':1, '아스날': 1, '아스널': 1,'Brighton & Hov…': 2, '브라이튼': 2,'Burnley':3, '번리': 3,'Cardiff City':4, '카디프시티': 4,'Chelsea':5, '첼시': 5,
                'Crystal Palace':6, '크리스탈 팰리스': 6,'Everton':7,  '에버턴': 7, '에버튼': 7, 'Fulham':8, '풀햄': 8, 'Huddersfield Town':9, '허드슨타운': 9, 'Leicester City':10, '레스터': 10, '레스터시티': 10,
                '리버풀': 11,'Manchester City':12,  '맨체스터 시티': 12, '맨시티': 12, 'Manchester United':13, '맨체스터 유나이티드': 13, '맨유': 13, 'Newcastle United':14, '뉴캐슬': 14, '뉴캐슬 유나이티드': 14,
                'Southampton':15, '사우샘프턴': 15, 'Tottenham Hotspur':16,'Tottenham':16,  '토트넘': 16, '토튼햄': 16, '토트넘 핫스퍼': 16,'Watford':17,  '왓포드': 17, 'West Ham United':18, '웨스트햄': 18, '울버햄튼': 19,'Wolverhampton …':19, '울버햄턴': 19}

command_options = {'전체':0, '정보':1, '순위':2, '일정':3, '결과':4 , '예상':5, '예측':5, '전체순위':0, 'Rank':2}

sample_command_list = ['리버풀과 토트넘', '맨유와 아스날의 순위를 알려줘', '번리의 다음 경기일정좀', '전체 순위 보여줘',
                       '리버풀, 맨시티, 왓포드의 현재 순위를 알려줘', '뉴캐슬의 경기결과 알려줘', '너 바보냐']
logo_url = []
#=====================================================================================
#                               크롤링 & 데이터
#=====================================================================================
def start():
    for a in soup.find_all("table", class_="leaguetable sortable table detailed-table"):
        rank = 1
        for col in a.find_all("tbody"):
            for tr in col.find_all("tr"):

                team = []
                team.append(rank)
                team_url = ""
                for data in tr.find_all("td", "text team large-link"):
                    team.append(data.get_text())
                    for hre in data.find_all("a"):
                        urls.append("https://us.soccerway.com" + hre.get("href"))
                for data in tr.find_all("td", "number total mp"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number total won total_won"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number total drawn total_drawn"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number total lost total_lost"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number total gf total_gf"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number total ga total_ga"):
                    team.append(data.get_text())
                for data in tr.find_all("td", "number points"):
                    team.append(data.get_text())

                # 최근 경기 5결과
                recent5game = []
                for data in tr.find_all("td", "form"):
                    for a in data.find_all("a"):
                        game = []
                        game.append(a.get("title"))
                        game.append(a.get_text().strip())
                        recent5game.append(game)
                    team.append(recent5game)
                teams.append(team)
                rank += 1


    # 딕셔너리 형태로 변경
    # 출력 형태 = teams["팀이름"] = [랭크, w, d, l, g, gf, p, recent5game ]

    for team in teams:
        team_dic = []
        team_dic.append(team[0])
        for i in range(2, 10):
            team_dic.append(team[i])
        teams_dic[team[1]] = team_dic

#   전체 순위 정보
def show_tables():
    ans = ()
    answer = []
    i = 0
    for a in teams_dic:
        # print(a)
        ans = (a , "\n\n*" + str(i+1) + "\t등 - " + teams_dic[a][2] + " 승  " + teams_dic[a][3] + "무  " + teams_dic[a][4] + " 패*\n" + "*득\t실 : " + teams_dic[a][5] +" : "+ teams_dic[a][6] + "\t점수 : " + teams_dic[a][7] + "*")
        i += 1
        answer.append(ans)
    return answer


# 팀 순위(기본정보)
def teamrankview(team):
    return teams_dic[team][0]


def show_rank(team_list):
    answer = []
    for team in team_list:
        teaminfo = ""
        teaminfo += ("*" + team + "의 순위는 " + str(teamrankview(team) + 1) + "위 입니다.*\n")
        data = (team, teaminfo)
        answer.append(data)
    return answer


def teaminformation(parameter):
    i = 0
    answer = "*순    위\t:\t" + str(teams_dic[parameter][i])
    i += 1
    answer += "*\n*경기수\t:\t" + str(teams_dic[parameter][i])
    i += 1
    answer += "*\n*전    적\t:\t"
    answer += teams_dic[parameter][i] + "승 "
    i += 1
    answer += teams_dic[parameter][i] + "무 "
    i += 1
    answer += teams_dic[parameter][i] + "패"
    i += 1
    answer += "*\n*득    점\t:\t" + teams_dic[parameter][i]
    i += 1
    answer += "*\n*실    점\t:\t" + teams_dic[parameter][i]
    i += 1
    answer += "*\n*포 인 트  :\t" + teams_dic[parameter][i]
    answer += "*"
    return (parameter, answer)


# 팀 상세정보
def show_info(team_list):
    answer = []
    for team in team_list:
        answer.append(teaminformation(team))
    return answer


#=======================================================================================
def expectgame(url_index):
# 경기 일정
    expect5game = ""
    exp_game = BeautifulSoup(urllib.request.urlopen(urls[url_index - 1]).read(), "html.parser")
    for data in exp_game.find_all("table", "matches"):
        for tbody in data.find_all("tbody"):
            # 구성 : 요일, 날짜, 팀A, 팀B, 시간

            i = 1
            for tr in tbody.find_all("tr"):
                expect = ""
                if i < 6:
                   i += 1
                else:
                    for td in tr.find_all("td", "day no-repetition"):
                        expect += ("\n요  일\t:\t" + (td.get_text()))
                    for td in tr.find_all("td", "full-date"):
                        expect += ("\n날  짜\t:\t" + (td.get_text()))
                    for td in tr.find_all("td", "team team-a "):
                        expect += ("\n경  기\t:\t" + (td.get_text().strip()))
                    for td in tr.find_all("td", "team team-b "):
                        expect += ("\t vs \t "+(td.get_text().strip()))
                    for td in tr.find_all("td", "score-time status"):
                        for time in td.find_all("a"):
                            expect += ("\n시  간\t:\t"+(time.get_text().strip()) + "\n")
                    expect5game += (expect)
    return expect5game

# 다음 경기일정
def show_schedules(team_list):
    answer = []
    for team in team_list:
        ans = (team, expectgame(teams_dic[team][0]))
        answer.append(ans)
    return answer


# 경기 결과
def show_result(team_list):
    answer = "* \t\t\t\t홈\tvs\t어웨이*"
    dat = []
    ans = ()
    for team in team_list:
        for data in teams_dic[team][8]:

            answer += "\n *경   기\t:\t" + data[0]
            if data[1] == "W":
                answer += "\t\t\t\t승  리*\n"
            else :
                answer += "\t\t\t\t패  배*\n"
        ans = (team, answer)
        dat.append(ans)
    return dat

def show_toto(team_list):
    answer = ""



    return answer


def test_funtion(command, keyword_team, keyword_option):
    for word in command.split():

        # 특수문자 제거
        for symbol in punctuation:
            word = word.replace(symbol, '')

        # 조사 제거
        for key in team_name_kr.keys():
            if word.startswith(key):
                keyword_team.append(team_name_en[int(team_name_kr.get(key))])

        # 목적 정보 입력
        for op in command_options.keys():
            if word.__contains__(op):
                if op == '순위' and keyword_option.__contains__('전체'):
                    continue
                else :
                    keyword_option.append(command_options.get(op))


def excute_fun(keyword_team, keyword_option):
    ret_val = []
    answer = []
    information = ""
    # 실행 함수 분기
    if len(keyword_team) == 0 | len(keyword_option) == 0:
        return ["무슨 말인지 모르겠어요ㅠ 질문을 다시 해주세요!"]
    elif len(keyword_option) == 0:
        information = "팀 정보"
        answer = show_info(keyword_team)
        ret_val.append((information, answer))
        return ret_val


    # '전체':0, '정보':1, '순위':2, '일정':3, '결과':4
    for op in keyword_option:
        if op == 0:
            information = "*전체 순위*"
            answer = show_tables()
        elif op == 1:
            information = "*팀 정보*"
            answer = show_info(keyword_team)
        elif op == 2:
            information = "*팀 순위*"
            answer = show_rank(keyword_team)
        elif op == 3:
            information = "*팀 경기 일정*"
            answer = show_schedules(keyword_team)
        elif op == 4:
            information = "*팀 경기 5 결과*"
            answer = show_result(keyword_team)
        elif op == 5:
            answer = show_toto(keyword_team)
        ret_val.append((information, answer))
    return ret_val


#=====================================================================================
#                  # 크롤링 함수 구현하기 - 출력하는 부분
#=====================================================================================

def _crawl_naver_keywords(command):
# def test_case(command):
    information = ""
    command = u' '.join(command.split()[1:])
    answer = []
    keyword_team = []
    keyword_option = []
    print('Command: ', end='')
    print(command)
    test_funtion(command, keyword_team, keyword_option)
    answer = excute_fun(keyword_team, keyword_option)
    print('Answer : ', end='')
    print(answer)
    print('==============================')
    print(command)
 #   한글 지원을 위해 앞에 unicode u를 붙혀준다.
 #    return u'\n'.join(answer)
    return answer
# =====================================================================================
#                  # 크롤링 함수 구현하기 - 출력하는 부분(완료)
# =====================================================================================

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        information = ""
        keywords = []
        keywords = _crawl_naver_keywords(text)

        #keywords[0] - text
        #keywords[1] - attachment
        #("팀 이름", "팀 정보")

        for keyword in keywords:
            message_attachments = []

            print(keyword)

            for a in keyword[1] :
                print(a)
                if a[1] is None:
                    continue

                R = str(hex(random.randrange(0, 256)))[2:]
                G = str(hex(random.randrange(0, 256)))[2:]
                B = str(hex(random.randrange(0, 256)))[2:]
                img_url = ""
                exp_game = BeautifulSoup(urllib.request.urlopen(urls[teams_dic[a[0]][0] - 1]).read(), "html.parser")
                for data in exp_game.find_all("div", "logo"):
                    for src in data.find_all("img"):
                        img_url = src.get("src")

                message = dict(color="#" + R + G + B, title=a[0],
                               title_link=str(urls[teams_dic[a[0]][0] - 1]), text=a[1], thumb_url=img_url)

                message_attachments.append(message)

            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keyword[0],
                attachments=message_attachments

            )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    start()
    app.run('0.0.0.0', port=5000)