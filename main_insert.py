
# 1. import
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
import uvicorn # 서버
from sqlalchemy import create_engine
from fastapi.templating import Jinja2Templates

# 2. DB 커넥션
db_connection = create_engine('mysql://test:1234@127.0.0.1:3306/test')

# 3. template 폴더 마운트
templates = Jinja2Templates(directory="templates")

# 4. fastapi 인스턴스 생성
app = FastAPI()

################# 페이지 라우팅 #################

# 5. 게시판 리스트 (메인 페이지)
@app.get('/')
def list_page(request: Request):
  # 페이지 열리기 전 DB조회하여 프론트로 리스트 응답
  query = db_connection.execute('select * from content order by c_id DESC') # 내림차순(최신순) 정렬
  contents = query.fetchall()

  result = []
  
  for content in contents:
    temp = {
      'c_id': content[0],
      'c_title': content[1], 
      'c_text': content[2],
      'user_id': content[3],
      'date': content[4],
    }
    result.append(temp)

  # 페이지 반환
  return templates.TemplateResponse('index.html', context={'request': request, 'contents': result})

# 6. 게시판 작성
# 게시글을 작성하는 페이지
@app.get('/write')
def write_page(request: Request):
  # 페이지 반환
  return templates.TemplateResponse('write.html', context={'request': request})


################# 페이지 라우팅 #################

# 6-1. 게시판 작성 처리
@app.post('/write')
def write_content(
    title: Annotated[str,Form()],
    text: Annotated[str,Form()],
    user_id: Annotated[str,Form()]):
  #현재 날짜 가져오기
  # current_date = datetime.now().strtfime('%Y-%m-%d %H-%M-%S')
  current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # DB에 추가
  db_connection.execute('insert into content (c_title, c_text ,user_id , date) values (%s, %s, %s, %s)', (title, text, user_id, current_date))

  # 목록 페이지로 리다이렉트
  return RedirectResponse(url='/', status_code=303)

# 7. 게시판 상세
# 프론트에서 클릭시 id 받아돠서 select wher절로 조회하여 detail정보 넘기기
# @app.get('/content')

# 8. 게시판 삭제
# @app.get('/delete')

if __name__ == '__main__':
  print('서버ON')
  uvicorn.run(app, host='localhost', port=8080)

