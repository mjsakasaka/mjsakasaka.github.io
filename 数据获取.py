# -*- coding: utf-8 -*-
# Created on 2020/6/1
# @author: mengru
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os


def getHTMLText(url, code='utf-8', params=None):
    try:
        r = requests.get(url, params)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        print("")


def fetchCityInfo(info_list, html, city_list):
    soup = BeautifulSoup(html, 'html.parser')
    soup2 = soup.find(attrs={"class": "b_place_index", "id": "placebottomNav"}).dl.next_sibling
    tag_list = soup2.find_all('dd')
    for tag in tag_list:
        ttl = tag.a.attrs['title'].replace('旅游攻略', '')
        if ttl in city_list:
            city_name = ttl
            city_id = tag.a.attrs['href'].split(r'/')[-1][4:10]
            info_list.append([city_name, city_id])


def fetchCommentInfo(date_list, city_id, city_name, start_date, end_date):
    root = city_name + r'/'
    if not os.path.exists(root):
        os.mkdir(root)

    start_url = r'http://travel.qunar.com/place/api/html/comments/dist/'
    kv = {'sortField': 0, 'pageSize': 10, 'page': 1}
    cmt_url = start_url + city_id
    for i in range(1, 27):
        try:
            date = ''
            kv['page'] = i
            cmt_html = getHTMLText(cmt_url, params=kv)
            print(i)
            lst = re.findall(r'http://travel.qunar.com/p-pl\d{7}', cmt_html)
            cmtpg_url_list = []
            for i in lst:
                if not i in cmtpg_url_list:
                    cmtpg_url_list.append(i)
            for cmtpg_url in cmtpg_url_list:
                cmtpg_html = getHTMLText(cmtpg_url)
                soup = BeautifulSoup(cmtpg_html, 'html.parser')
                content = soup.find_all('div', attrs={'class': 'comment_content'})
                div = soup.find('div', attrs={'class': 'e_comment_add_info'})
                li = div('li')
                match = re.search(r'\d{4}-\d{2}-\d{2}', str(li))
                if match:
                    date = match.group(0)

                if date < start_date:
                    break
                if end_date >= date >= start_date:
                    date_list.append(date)
                    path = root + date + '.txt'
                    i = 0
                    while os.path.exists(path):
                        i += 1
                        path = root + date + f'({i})' + '.txt'
                    with open(path, 'w', encoding='utf-8-sig') as f:
                        f.write(str(content))

            if date < start_date:
                break
        except:
            continue


def formCityDf(date_list, city_name, city_id):
    city_df = pd.DataFrame(date_list, index=range(1, len(date_list) + 1), columns=['CommentDate'])
    city_df['City'] = city_name
    city_df['CityID'] = city_id
    mark = [item[:7] for item in city_df.CommentDate]
    city_df['Month'] = mark
    return city_df[['City', 'CityID', 'Month', 'CommentDate']]


def main():
    sf_url = r'http://travel.qunar.com/p-sf297555-jiangsu'
    sf_html = getHTMLText(sf_url)
    c_info = []
    c_list = ['徐州', '宿迁', '连云港', '淮安', '盐城', '扬州', '泰州', '南通', '镇江', '常州', '无锡', '苏州', '南京']
    fetchCityInfo(c_info, sf_html, c_list)

    col = ['City', 'CityID', 'Month', 'CommentDate']
    header = pd.DataFrame([[0, 0, 0, 0]], columns=col).drop(0)
    header.to_csv('data.csv', encoding='utf-8-sig')

    for c in c_info:
        d_list = []
        c_name = c[0]
        c_id = c[1]
        fetchCommentInfo(d_list, c_id, c_name, start_date='2019-12-01', end_date='2020-05-30')
        c_df = formCityDf(d_list, c_name, c_id)
        c_df.to_csv('data.csv', mode='a', header=False, encoding='utf-8-sig')


main()
