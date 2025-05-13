
# 1. import
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Form
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

# 7. 게시판 상세
# 프론트에서 클릭시 id 받아돠서 select wher절로 조회하여 detail정보 넘기기
@app.get('/content/{content_id}')
async def get_detail(request: Request, content_id: int):
  # DB에서 조회
  query = db_connection.execute(f'select * from content where c_id = {content_id}')
  content = query.fetchone()
  print('content', content)

  # 게시글 존재하지 않는경우
  if content is None:
    raise HTTPException(status_code=404, detail='Content not found')
  
  result = {
    'c_id': content[0],
    'c_title': content[1], 
    'c_text': content[2],
    'user_id': content[3],
    'date': content[4],
  }

  # 페이지 반환
  return templates.TemplateResponse('detail.html', context={'request': request, 'content': result})



################# 페이지 라우팅 #################

# Content 형태 정의
class Content(BaseModel):
  title: str
  text: str
  user_id: str
  # current_date: str = None  # 선택적 필드

# 6-1. 게시판 작성 처리
@app.post('/write')
def write_content(title: Annotated[str, Form()],
    text: Annotated[str, Form()],
    user_id: Annotated[str, Form()]):
  
  #현재 날짜 가져와서 문자열로 변환
  current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # DB에 추가
  db_connection.execute('insert into content (c_title, c_text ,user_id , date) values (%s, %s, %s, %s)', (title, text, user_id, current_date))

  # 목록 페이지로 리다이렉트
  return RedirectResponse(url='/', status_code=303)


# 8. 게시판 삭제
@app.delete('/content/{content_id}')
async def delete_content(content_id: str):
  # 삭제할 게시글 존재하는지 확인
  query = db_connection.execute(f'select * from content where c_id = {content_id}')
  content = query.fetchone()
  print('content', content)

  # 게시글 존재하지 않는 경우 404에러
  if content is None:
    print('존재하지 않음')
    raise HTTPException(status_code=404, detail='Content not found')
  
  # 게시글 삭제
  db_connection.execute(f'delete from content where c_id = {content_id}')

  return {'message': 'Content deleted successfully'}

  # 목록 페이지로 리다이렉트
  # return RedirectResponse(url='/', status_code=303)


if __name__ == '__main__':
  print('서버ON')
  uvicorn.run(app, host='localhost', port=8080)

