# coding='utf-8'

import requests
from lxml import etree
import re
from io import BytesIO
from fontTools.ttLib import TTFont
from knn_font import Classify


classify = Classify()

def get_map(text):
    font_url = 'http:' + re.findall(r"url\('(.*?\.woff)'\)", text)[0]
    content = requests.get(font_url).content
    with open('./fonts/test.woff', 'wb') as f:
        f.write(content)
    font = TTFont(BytesIO(content))
    glyf_order = font.getGlyphOrder()[2:]

    info = list()
    for g in glyf_order:
        coors = font['glyf'][g].coordinates
        coors = [_ for c in coors for _ in c]
        info.append(coors)
    map_li = map(lambda x: str(int(x)), classify.knn_predict(info))
    uni_li = map(lambda x: x.lower().replace('uni', '&#x') + ';', glyf_order)
    return dict(zip(uni_li, map_li))


def get_board():
    url = 'https://maoyan.com/board/1'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
    }
    text = requests.get(url, headers=headers).text

    map_dict = get_map(text)
    for uni in map_dict.keys():
        text = text.replace(uni, map_dict[uni])

    html = etree.HTML(text)
    dd_li = html.xpath('//dl[@class="board-wrapper"]/dd')
    for dd in dd_li:
        p_li = dd.xpath(
            './div[@class="board-item-main"]//div[@class="movie-item-info"]/p')
        title = p_li[0].xpath('./a/@title')[0]
        star = p_li[1].xpath('./text()')[0]
        releasetime = p_li[2].xpath('./text()')[0]

        p_li = dd.xpath(
            './div[@class="board-item-main"]//div[@class="movie-item-number boxoffice"]/p')
        realtime_stont = ''.join(
            list(map(lambda x: x.strip(), p_li[0].xpath('.//text()'))))
        total_stont = ''.join(
            list(map(lambda x: x.strip(), p_li[1].xpath('.//text()'))))
        print(title)
        print(star)
        print(releasetime)
        print(realtime_stont)
        print(total_stont)
        print('-' * 50)


if __name__ == '__main__':
    get_board()
