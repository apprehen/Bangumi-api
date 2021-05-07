import os
import tempfile
import time
import zipfile
from pathlib import Path
import uvicorn
from fastapi import FastAPI
import pandas as pd
import httpx
import response_code as Response

app = FastAPI()
FILE_PATH = str(str(Path.cwd()) + os.sep + 'data' + os.sep)

cache_time = 60 * 60 * 6
bangumi_data_json = {
    # '202104':{
    #     'data':[],
    #     'last_cache_time':0.0
    # }
}
last_check_time = 0.0


def log_error(e):
    print(f'错误：{e}')


def log_info(e):
    print(f'信息：{e}')


# 下载zip文件，返回文件地址
async def download_zip_to_xlsx(date: str) -> str:
    if len(date) != 6:
        return None
    url = f'https://hmacg.cn/bangumi/xfb.php?dl={date}&type=all&ext=xlsx'
    async with httpx.AsyncClient(proxies={}) as client:
        try:
            res = await client.get(url)
            _tmp_file = tempfile.TemporaryFile()  # 创建临时文件
            _tmp_file.write(res.content)  # byte字节数据写入临时文件
            with zipfile.ZipFile(_tmp_file, 'r') as f:
                for fn in f.namelist():
                    extracted_path = Path(f.extract(fn, FILE_PATH))
                    # file_name = fn.encode('cp437').decode('gbk')
                    file_name = f'{date}.xlsx'
                    if os.path.exists(FILE_PATH + file_name):
                        os.remove(FILE_PATH + file_name)
                        continue
                    extracted_path.rename(FILE_PATH + file_name)
                    return file_name
        except Exception as e:
            log_error(e)
            return None


# 异步求余查询
async def xlsx_to_json(file_name: str):
    names = ['Unnamed: 0', 'Unnamed: 1', '番名', '星期', '时间',
             'bilibili', 'AcFun', '优酷', '爱奇艺', '腾讯',
             '独播', '首播', '集数', '特殊', '标签',
             'Unnamed: 15', 'Unnamed: 16']
    sheet = pd.read_excel(FILE_PATH + file_name, names=names, skiprows=2, skipfooter=10, keep_default_na=False)
    ret_dic = [
        {'weekday': '星期一', 'items': []},
        {'weekday': '星期二', 'items': []},
        {'weekday': '星期三', 'items': []},
        {'weekday': '星期四', 'items': []},
        {'weekday': '星期五', 'items': []},
        {'weekday': '星期六', 'items': []},
        {'weekday': '星期天', 'items': []},
        {'weekday': '其他', 'items': []}]
    for i in sheet.index.values:
        copyright = sheet.loc[i, ['bilibili', 'AcFun', '优酷', '爱奇艺', '腾讯',
                                  '独播']].to_dict()
        tmp = sheet.loc[i, ['番名', '星期', '时间',
                            '首播', '集数', '特殊', '标签']].to_dict()
        tmp.update({'版权': copyright})
        if tmp['番名'] == '新番表 by Hazx.':
            continue
        if tmp['特殊'] == '全集更新':
            ret_dic[7]['items'].append(tmp)
            continue
        if tmp['星期'] == '周一':
            ret_dic[0]['items'].append(tmp)
        elif tmp['星期'] == '周二':
            ret_dic[1]['items'].append(tmp)
        elif tmp['星期'] == '周三':
            ret_dic[2]['items'].append(tmp)
        elif tmp['星期'] == '周四':
            ret_dic[3]['items'].append(tmp)
        elif tmp['星期'] == '周五':
            ret_dic[4]['items'].append(tmp)
        elif tmp['星期'] == '周六':
            ret_dic[5]['items'].append(tmp)
        elif tmp['星期'] == '周日':
            ret_dic[6]['items'].append(tmp)
        else:
            ret_dic[7]['items'].append(tmp)
    return ret_dic


async def get_xlsx(date: str):
    if os.path.exists(FILE_PATH + f'{date}.xlsx'):
        os.remove(FILE_PATH + f'{date}.xlsx')
    log_info(f'获取 {date}.xlsx 中...')
    file_name = await download_zip_to_xlsx(date)
    return await xlsx_to_json(file_name)


async def get_data_json(date: str) -> list:
    global bangumi_data_json
    if tmp:=bangumi_data_json.get(date):
        if time.time() - tmp['last_cache_time'] >= cache_time:
            # 缓存过期
            log_info('缓存过期，或不存在数据')
            tmp['last_cache_time'] = time.time()
            tmp['data'] = await get_xlsx(date)
            bangumi_data_json.update(tmp)
        else:
            log_info('命中缓存')
            return tmp['data']
    else:
        bangumi_data_json.update({
            date:{
                'data':await get_xlsx(date),
                'last_cache_time':time.time()
            }
        })

    return bangumi_data_json.get(date)['data']


# 获取每周番剧
@app.get("/api/calendar/{year}/{month}")
async def get_date_json(year: str, month: str):
    if len(year) != 4 or len(month) != 2:
        return Response.resp_400(data=None, message='参数错误！')
    try:
        return Response.resp_200(data=await get_data_json(year + month))
    except Exception as e:
        return Response.resp_400(data=None, message=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
