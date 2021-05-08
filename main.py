import datetime

import uvicorn
from fastapi import FastAPI

from utils import response_code as Response
from utils.get_data import get_data_json

app = FastAPI()


# 获取每周番剧
@app.get("/api/calendar/{year}/{month}")
async def get_date_json(year: str, month: str):
    if len(year) != 4 or len(month) != 2 or month not in ['01', '04', '07', '10']:
        return Response.resp_400(data=None, message='参数错误！')
    return Response.resp_200(data=await get_data_json(year + month))


# 获取每周番剧
@app.get("/")
async def index():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    _date = str(year)
    if month < 4:
        _date += '01'
    elif month < 7:
        _date += '04'
    elif month < 10:
        _date += '07'
    elif month <= 12:
        _date += '10'
    return Response.resp_200(data=await get_data_json(_date))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
