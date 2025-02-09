from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import cv2
import dlib
from collections import defaultdict
import random

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/images/uploaded/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Dlib의 얼굴 검출기와 랜드마크 예측기 초기화
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # 다운로드한 모델 파일 경로
subjects = [
    {"name": "글로벌금융경영학부", "url": "https://globaladm.smu.ac.kr/globaladm/index.do"},
    {"name": "경영공학과", "url": "https://me.smu.ac.kr/me/index.do"},
    {"name": "건설시스템공학과", "url": "https://civil.smu.ac.kr/civil/index.do"},
    {"name": "간호학과", "url": "https://nursing.smu.ac.kr/nursing/index.do"},
    {"name": "사회체육전공", "url": "https://sportforall.smu.ac.kr/sportforall/index.do"},
    {"name": "문화예술경영전공", "url": "https://culturalart.smu.ac.kr/culturalart/index.do"},
    {"name": "영화영상전공", "url": "https://movie.smu.ac.kr/movie/index.do"},
    {"name": "디지털콘텐츠전공", "url": "https://digitalcontents.smu.ac.kr/digital/index.do"},
    {"name": "소프트웨어학과", "url": "https://software.smu.ac.kr/software/index.do"},
    {"name": "정보보안공학과", "url": "https://dis.smu.ac.kr/dis/index.do"},
    {"name": "시스템반도체공학과", "url": "https://sse.smu.ac.kr/sse/index.do"},
    {"name": "전자공학과", "url": "https://primeee.smu.ac.kr/primeee/index.do"},
    {"name": "스마트정보통신공학과", "url": "https://ittech.smu.ac.kr/it/index.do"},
    {"name": "인더스트리얼디자인전공", "url": "https://www.smu.ac.kr/industrial/index.do"},
    {"name": "패션디자인전공", "url": "https://fashion.smu.ac.kr/fashion/index.do"},
    {"name": "사진영상미디어전공", "url": "https://photo.smu.ac.kr/photo/index.do"},
    {"name": "세라믹디자인전공", "url": "https://ceramic.smu.ac.kr/ceramic/index.do"},
    {"name": "디지털만화영상전공", "url": "https://dcartoonani.smu.ac.kr/cartoonani/index.do"},
    {"name": "그린화학공학과", "url": "https://green.smu.ac.kr/green/index.do"},
    {"name": "스포츠경영전공", "url": "https://sportindustry.smu.ac.kr/sportindustry/index.do"},
    {"name": "AR·VR미디어디자인전공", "url": "https://arvr.smu.ac.kr/arvr/index.do"},
    {"name": "연극전공", "url": "https://dramatics.smu.ac.kr/dramatics/index.do"},
    {"name": "그린스마트시티학과", "url": "https://greensmartcity.smu.ac.kr/greensmartcity/index.do"},
    {"name": "행정학부", "url": "https://public.smu.ac.kr/public/index.do"},
    {"name": "국가안보학과", "url": "https://www.smu.ac.kr/sdms/index.do"},
    {"name": "경영학부", "url": "https://smubiz.smu.ac.kr/smubiz/index.do"},
    {"name": "경제금융학부", "url": "https://econo.smu.ac.kr/economic/index.do"},
    {"name": "핀테크전공", "url": "https://fbs.smu.ac.kr/fbs/index.do"},
    {"name": "가족복지학과", "url": "https://smfamily.smu.ac.kr/smfamily/index.do"},
    {"name": "교육학과", "url": "https://learning.smu.ac.kr/peda/index.do"},
    {"name": "국어교육과", "url": "https://koredu.smu.ac.kr/koredu/index.do"},
    {"name": "수학교육과", "url": "https://mathed.smu.ac.kr/mathedu/index.do"},
    {"name": "문헌정보학전공", "url": "https://libinfo.smu.ac.kr/libinfo/index.do"},
    {"name": "역사콘텐츠전공", "url": "https://history.smu.ac.kr/history/index.do"},
    {"name": "한일문화콘텐츠전공", "url": "https://kjc.smu.ac.kr/kjc/index.do"},
    {"name": "생활예술전공", "url": "https://smulad.smu.ac.kr/smulad/index.do"},
    {"name": "음악학부", "url": "https://music.smu.ac.kr/music/index.do"},
    {"name": "빅데이터융합전공", "url": "https://fbs.smu.ac.kr/fbs/index.do"},
    {"name": "지능IOT융합전공", "url": "https://aiot.smu.ac.kr/aiot/index.do"},
    {"name": "스마트생산전공", "url": "https://fbs.smu.ac.kr/fbs/index.do"},
    {"name": "화학에너지공학전공", "url": "https://energy.smu.ac.kr/cee/index.do"},
    {"name": "컴퓨터과학전공", "url": "https://cs.smu.ac.kr/cs/index.do"},
    {"name": "전기공학전공", "url": "https://electric.smu.ac.kr/electric/index.do"},
    {"name": "화공신소재전공", "url": "https://ichem.smu.ac.kr/ichemistry/index.do"},
    {"name": "조형예술전공", "url": "https://finearts.smu.ac.kr/finearts/index.do"},
    {"name": "무용예술전공", "url": "https://dance.smu.ac.kr/dance/index.do"},
    {"name": "의류학전공", "url": "https://fashionindustry.smu.ac.kr/clothing2/index.do"},
    {"name": "생명화학공학부", "url": "https://biotechnology.smu.ac.kr/biotechnology/index.do"},
    {"name": "스포츠건강관리전공", "url": "https://sports.smu.ac.kr/smpe/index.do"},
    {"name": "게임전공", "url": "https://game.smu.ac.kr/game01/index.do"},
    {"name": "애니메이션전공", "url": "https://animation.smu.ac.kr/animation/index.do"},
    {"name": "디자인융합학과", "url": "https://design.smu.ac.kr/design/index.do"},
    {"name": "글로벌경영학과", "url": "https://gbiz.smu.ac.kr/newmajoritb/index.do"},
    {"name": "융합경영학과", "url": "https://imgmt.smu.ac.kr/cm/index.do"},
    {"name": "사회복지학과", "url": "https://www.smu.ac.kr/wac/major/info3.do"},
    {"name": "문화콘텐츠문화경영학과", "url": "https://www.smu.ac.kr/gsct/department/info1.do"},
    {"name": "산업경영공학과", "url": "https://ie.inha.ac.kr/ie/969/subview.do"},
    {"name": "기계공학과", "url": "https://mech.inha.ac.kr/mech/index.do"},
    {"name": "전기공학과", "url": "https://electrical.inha.ac.kr/electrical/index.do"},
    {"name": "화학공학과", "url": "https://chemeng.inha.ac.kr/chemeng/index.do"},
    {"name": "건축학부(건축공학)", "url": "https://arch.inha.ac.kr/arch/2155/subview.do"},
    {"name": "경영학과", "url": "https://biz.inha.ac.kr/biz/index.do"},
    {"name": "글로벌금융학과", "url": "https://gfiba.inha.ac.kr/gfiba/index.do"},
    {"name": "간호학과", "url": "https://nursing.inha.ac.kr/nursing/index.do"},
    {"name": "사회복지학과", "url": "https://welfare.inha.ac.kr/welfare/index.do"},
    {"name": "아동심리학과", "url": "https://child.inha.ac.kr/child/index.do"},
    {"name": "식품영양학과", "url": "https://foodnutri.inha.ac.kr/foodnutri/index.do"},
    {"name": "교육학과", "url": "https://education.inha.ac.kr/education/index.do"},
    {"name": "체육교육과", "url": "https://physicaledu.inha.ac.kr/physicaledu/index.do"},
    {"name": "문화콘텐츠문화경영학과", "url": "https://culturecm.inha.ac.kr/culturecm/7877/subview.do"},
    {"name": "연극영화학과", "url": "https://theatrefilm.inha.ac.kr/theatrefilm/9550/subview.do"},
    {"name": "사학과", "url": "https://history.inha.ac.kr/history/index.do"},
    {"name": "한국어문학과", "url": "https://korean.inha.ac.kr/korean/index.do"},
    {"name": "소프트웨어융합공학과", "url": "https://swcc.inha.ac.kr/act/index.do"},
    {"name": "반도체시스템공학과", "url": "https://sse.inha.ac.kr/sse/index.do"},
    {"name": "미래자동차공학(융합전공)", "url": "https://fveng.inha.ac.kr/user/fve/"},
    {"name": "데이터사이언스학과", "url": "https://datascience.inha.ac.kr/datascience/index.do"},
    {"name": "인공지능공학과", "url": "https://doai.inha.ac.kr/doai/index.do"},
    {"name": "컴퓨터공학과", "url": "https://cse.inha.ac.kr/cse/index.do"},
    {"name": "항공우주공학과", "url": "https://aerospace.inha.ac.kr/aerospace/index.do"},
    {"name": "메카트로닉스공학과", "url": "https://fccollege.inha.ac.kr/fccollege/8130/subview.do"},
    {"name": "조선해양공학과", "url": "https://naoe.inha.ac.kr/naoe/index.do"},
    {"name": "스마트모빌리티공학과", "url": "https://sme.inha.ac.kr/sme/index.do"},
    {"name": "조형예술학과", "url": "https://finearts.inha.ac.kr/finearts/index.do"},
    {"name": "의류디자인학과", "url": "https://fashion.inha.ac.kr/fashion/index.do"},
    {"name": "디자인융합학과", "url": "https://artsports.inha.ac.kr/artsports/9582/subview.do"},
    {"name": "사진영상미디어전공", "url": "https://designtech.inha.ac.kr/designtech/3068/subview.do"},
    {"name": "세라믹디자인전공", "url": "https://dmse.inha.ac.kr/dmse/2085/subview.do"},
    {"name": "문학과", "url": "https://korean.inha.ac.kr/korean/index.do"},
    {"name": "철학과", "url": "https://philosophy.inha.ac.kr/philosophy/index.do"},
    {"name": "수학과", "url": "https://math.inha.ac.kr/math/index.do"},
    {"name": "물리학과", "url": "https://physics.inha.ac.kr/physics/index.do"},
    {"name": "통계학과", "url": "https://statistics.inha.ac.kr/statistics/index.do"},
    {"name": "화학과", "url": "https://chemistry.inha.ac.kr/chemistry/index.do"},
    {"name": "신소재공학과", "url": "https://dmse.inha.ac.kr/dmse/index.do"},
    {"name": "스포츠과학과", "url": "https://sport.inha.ac.kr/sport/index.do"},
    {"name": "AR·VR미디어디자인전공", "url": "https://designtech.inha.ac.kr/designtech/index.do"},
    {"name": "산업경영학과", "url": "https://fccollege.inha.ac.kr/fccollege/index.do"},
    {"name": "패션디자인전공", "url": "https://fashion.inha.ac.kr/fashion/index.do"},
    {"name": "미디어커뮤니케이션학과", "url": "https://comm.inha.ac.kr/comm/index.do"},
    {"name": "영화영상전공", "url": "https://theatrefilm.inha.ac.kr/theatrefilm/index.do"},
    {"name": "디지털콘텐츠전공", "url": "https://comm.inha.ac.kr/comm/index.do"},
    {"name": "글로벌금융학과", "url": "https://gfiba.inha.ac.kr/gfiba/index.do"},
    {"name": "융합기술경영학부", "url": "https://www.inha.ac.kr/kr/990/subview.do?&enc=Zm5jdDF8QEB8JTJGZGVwYXJ0bWVudEludHJvJTJGa3IlMkY0MSUyRjM1JTJGaW50cm9WaWV3LmRvJTNGZmxhZyUzRCUyNg=="},
    {"name": "금융투자학과", "url": "https://www.inha.ac.kr/kr/997/subview.do?&enc=Zm5jdDF8QEB8JTJGZGVwYXJ0bWVudEludHJvJTJGa3IlMkY0OCUyRjc3JTJGaW50cm9WaWV3LmRvJTNG"}
]

# MBTI, 학과, 골든 레이시오 설정 (코드를 참고하여 정의)
# ... SEOUL, CHEONAN, INHA, MBTI, golen_ratio, etc.
SEOUL = {}
SEOUL["ISTJ"] = ["행정학부", "국가안보학과", "경영학부", "경제금융학부", "핀테크전공"]
SEOUL["ISFJ"] = ["가족복지학과", "교육학과", "국어교육과", "수학교육과", "문헌정보학전공"]
SEOUL["INFJ"] = ["역사콘텐츠전공", "한일문화콘텐츠전공", "생활예술전공", "문헌정보학전공", "음악학부"]
SEOUL["INTJ"] = ["빅데이터융합전공", "지능IOT융합전공", "스마트생산전공", "화학에너지공학전공", "컴퓨터과학전공"]
SEOUL["ISTP"] = ["스마트생산전공", "전기공학전공", "지능IOT융합전공", "컴퓨터과학전공", "화공신소재전공"]
SEOUL["ISFP"] = ["조형예술전공", "무용예술전공", "의류학전공", "음악학부", "생활예술전공"]
SEOUL["INFP"] = ["역사콘텐츠전공", "한일문화콘텐츠전공", "문헌정보학전공", "음악학부", "생활예술전공"]
SEOUL["INTP"] = ["생명화학공학부", "화학에너지공학전공", "빅데이터융합전공", "컴퓨터과학전공", "지능IOT융합전공"]
SEOUL["ESTP"] = ["스포츠건강관리전공", "게임전공", "애니메이션전공", "스마트생산전공", "컴퓨터과학전공"]
SEOUL["ESFP"] = ["무용예술전공", "조형예술전공", "의류학전공", "애니메이션전공", "음악학부"]
SEOUL["ENFP"] = ["역사콘텐츠전공", "한일문화콘텐츠전공", "디자인융합학과", "애니메이션전공", "생활예술전공"]
SEOUL["ENTP"] = ["빅데이터융합전공", "지능IOT융합전공", "컴퓨터과학전공", "스마트생산전공", "화학에너지공학전공"]
SEOUL["ESTJ"] = ["경영학부", "경제금융학부", "글로벌경영학과", "융합경영학과", "국가안보학과"]
SEOUL["ESFJ"] = ["가족복지학과", "교육학과", "국어교육과", "사회복지학과", "수학교육과"]
SEOUL["ENFJ"] = ["글로벌경영학과", "경제금융학부", "문화콘텐츠문화경영학과", "국가안보학과", "교육학과"]
SEOUL["ENTJ"] = ["경제금융학부", "글로벌경영학과", "융합경영학과", "스마트생산전공", "지능IOT융합전공"]

CHEONAN = {}
CHEONAN["ISTJ"] = ["글로벌금융경영학부", "경영공학과", "건설시스템공학과"]
CHEONAN["ISFJ"] = ["간호학과", "사회체육전공", "문화예술경영전공"]
CHEONAN["INFJ"] = ["문화예술경영전공", "영화영상전공", "디지털콘텐츠전공"]
CHEONAN["INTJ"] = ["소프트웨어학과", "정보보안공학과", "시스템반도체공학과"]
CHEONAN["ISTP"] = ["전자공학과", "스마트정보통신공학과", "인더스트리얼디자인전공"]
CHEONAN["ISFP"] = ["패션디자인전공", "사진영상미디어전공", "세라믹디자인전공"]
CHEONAN["INFP"] = ["디지털만화영상전공", "영화영상전공", "문화예술경영전공"]
CHEONAN["INTP"] = ["소프트웨어학과", "전자공학과", "그린화학공학과"]
CHEONAN["ESTP"] = ["스포츠경영전공", "사회체육전공", "AR·VR미디어디자인전공"]
CHEONAN["ESFP"] = ["패션디자인전공", "연극전공", "사진영상미디어전공"]
CHEONAN["ENFP"] = ["디지털콘텐츠전공", "영화영상전공", "문화예술경영전공"]
CHEONAN["ENTP"] = ["소프트웨어학과", "AR·VR미디어디자인전공", "정보보안공학과"]
CHEONAN["ESTJ"] = ["글로벌금융경영학부", "경영공학과", "그린스마트시티학과"]
CHEONAN["ESFJ"] = ["간호학과", "문화예술경영전공", "스포츠경영전공"]
CHEONAN["ENFJ"] = ["문화예술경영전공", "영화영상전공", "글로벌금융경영학부"]
CHEONAN["ENTJ"] = ["글로벌금융경영학부", "경영공학과", "스마트정보통신공학과"]

INHA = {}
INHA["ISTJ"] = ["산업경영공학과", "기계공학과", "전기공학과", "화학공학과", "건축학부(건축공학)", "경영학과", "글로벌금융학과"]
INHA["ISFJ"] = ["간호학과", "사회복지학과", "아동심리학과", "식품영양학과", "교육학과", "체육교육과"]
INHA["INFJ"] = ["문화콘텐츠문화경영학과", "연극영화학과", "사학과", "한국어문학과", "아동심리학과"]
INHA["INTJ"] = ["소프트웨어융합공학과", "반도체시스템공학과", "미래자동차공학(융합전공)", "데이터사이언스학과", "인공지능공학과", "컴퓨터공학과"]
INHA["ISTP"] = ["항공우주공학과", "메카트로닉스공학과", "조선해양공학과", "기계공학과", "스마트모빌리티공학과"]
INHA["ISFP"] = ["조형예술학과", "의류디자인학과", "디자인융합학과", "사진영상미디어전공", "세라믹디자인전공"]
INHA["INFP"] = ["문학과", "문화콘텐츠문화경영학과", "사학과", "철학과", "연극영화학과"]
INHA["INTP"] = ["수학과", "물리학과", "통계학과", "화학과", "신소재공학과"]
INHA["ESTP"] = ["스포츠과학과", "AR·VR미디어디자인전공", "산업경영학과", "경영학과"]
INHA["ESFP"] = ["연극영화학과", "패션디자인전공", "조형예술학과", "미디어커뮤니케이션학과"]
INHA["ENFP"] = ["영화영상전공", "문화콘텐츠문화경영학과", "디자인융합학과", "디지털콘텐츠전공"]
INHA["ENTP"] = ["소프트웨어융합공학과", "반도체시스템공학과", "미래자동차공학(융합전공)", "데이터사이언스학과"]
INHA["ESTJ"] = ["글로벌금융학과", "경영학과", "산업경영학과", "융합기술경영학부"]
INHA["ESFJ"] = ["교육학과", "사회복지학과", "아동심리학과", "체육교육과"]
INHA["ENFJ"] = ["문화콘텐츠문화경영학과", "연극영화학과", "글로벌금융학과", "미디어커뮤니케이션학과"]
INHA["ENTJ"] = ["경영학과", "산업경영학과", "스마트모빌리티공학과", "융합기술경영학부", "금융투자학과"]

MBTI = defaultdict(list)
MBTI["ISTJ"] = [1, 1, 1, -1, -1, 1, -1]
MBTI["ISFJ"] = [1, 1, -1, -1, -1, 1, 1]
MBTI["INFJ"] = [1, 1, 1, 1, 1, -1, -1]
MBTI["INTJ"] = [1, 1, 1, 1, 1, 1, -1]
MBTI["ISTP"] = [-1, -1, -1, 1, -1, -1, -1]
MBTI["ISFP"] = [-1, -1, -1, 1, -1, -1, 1]
MBTI["INFP"] = [1, -1, -1, 1, 1, -1, 1]
MBTI["INTP"] = [-1, 1, 1, 1, -1, 1, -1]
MBTI["ESTP"] = [-1, -1, 1, 1, -1, 1, 1]
MBTI["ESFP"] = [-1, -1, -1, 1, -1, 1, 1]
MBTI["ENFP"] = [1, -1, -1, 1, 1, -1, 1]
MBTI["ENTP"] = [-1, 1, 1, 1, 1, 1, 1]
MBTI["ESTJ"] = [1, 1, 1, -1, 1, 1, -1]
MBTI["ESFJ"] = [1, 1, -1, -1, -1, 1, 1]
MBTI["ENFJ"] = [1, 1, 1, 1, 1, -1, 1]
MBTI["ENTJ"] = [1, 1, 1, 1, 1, 1, -1]

face_MBTI = defaultdict(str)

face_MBTI["ISTJ"] = "미간이 넓기 때문에 논리적이고 신중하며, 신뢰할 수 있는 성격을 가졌습니다. 코가 길어 신중하고 보수적인 성향이 강하며, 눈썹이 길어서 합리적이고 온화한 성격을 나타냅니다. 눈이 작은 편이라 내성적이고, 자신을 표현하기보다는 차분하게 일을 처리하는 성격입니다. 눈꼬리가 내려가 있어 느긋하고 안정된 성격을 반영하며, 코가 넓어서 경제적 능력이 우수하고 외향적인 측면도 있습니다. 입술이 얇기 때문에 신념이 강하고, 확고한 성격을 가지고 있습니다."
face_MBTI["ISFJ"] = "미간이 차분하고 넓기 때문에 세심하고 책임감이 강한 성격을 가지고 있습니다. 코가 길어서 신중하고 보수적인 성향이 강하며, 눈썹이 짧아 이타적인 성향이 많지만 때로는 자기주장이 약할 수 있습니다. 눈이 작아 내성적이고 안정감을 중요시하며, 눈꼬리가 내려가 있어 느긋하고 타인을 배려하는 성격을 나타냅니다. 코가 넓어 외향적이고 현실적인 능력이 뛰어나며, 입술이 두꺼워 따뜻하고 정이 많고 감정 표현이 풍부합니다."
face_MBTI["INFJ"] = "미간이 차분하고 넓어서 직관적이며 미래지향적인 성격을 가지고 있습니다. 코가 길어 신중하고 깊이 있는 성격을 나타내며, 눈썹이 길어서 온화하고 합리적인 성격을 지녔습니다. 눈이 커서 감수성이 풍부하고 감정이 예민하며, 눈꼬리가 올라가 있어 신념과 목표가 확고하고 이를 이루기 위해 노력하는 성격입니다. 코가 좁아 예민하고 감수성이 뛰어나며, 입술이 얇아 신념이 확고하고 자신을 지키는 성격을 보여줍니다."
face_MBTI["ISTP"] = "미간이 좁아 실용적이고 논리적인 사고를 중시하는 성격을 가지고 있습니다. 코가 짧아서 융통성이 있으며 타협을 잘하는 성격을 나타냅니다. 눈썹이 짧아 자기중심적일 수 있지만 문제 해결 능력이 뛰어난 편입니다. 눈이 커서 개방적이고 감각이 예민하며, 눈꼬리가 내려가 있어 느긋하고 현재에 집중하는 성격을 보여줍니다. 코가 좁아서 예민하고 감각이 뛰어나며, 입술이 얇아 신념이 확고하고 차분한 성격을 지니고 있습니다."
face_MBTI["ISFP"] = "미간이 좁아서 감수성이 예민하고 독립적인 성격을 가지고 있습니다. 코가 짧아 타인과 잘 융화되며 유연한 사고를 지니고 있습니다. 눈썹이 짧아 때로는 이기적일 수 있지만 자신의 감정을 잘 표현하는 성격을 나타냅니다. 눈이 커서 감각이 예민하고 감수성이 발달한 성격을 지니며, 눈꼬리가 내려가 있어 느긋하고 여유로운 성격을 보입니다. 코가 좁아 감수성이 뛰어나고 예민하며, 입술이 두꺼워 정열적이고 강한 추진력을 가지고 있습니다."
face_MBTI["INFP"] = "미간이 차분하고 넓어서 이상적이고 감수성이 풍부한 성격을 가지고 있습니다. 코가 짧아 융통성이 있으며 낙천적인 성격을 나타내고, 눈썹이 짧아 때로는 자기중심적일 수 있지만 내적 가치관을 중요시합니다. 눈이 커서 감수성이 예민하고 신념이 강한 성격을 지니고 있으며, 눈꼬리가 올라가 있어 목표를 향한 열정과 의지가 강합니다. 코가 좁아 예민하고 감수성이 뛰어나며, 입술이 두꺼워 정열적이고 감정이 풍부한 성격을 가지고 있습니다."
face_MBTI["INTP"] = "미간이 좁아 분석적이고 이론적인 사고를 중시하는 성격을 가지고 있습니다. 코가 길어서 신중하며 자기주장이 강한 성격을 나타내고, 눈썹이 길어서 합리적이고 논리적인 성격을 지니고 있습니다. 눈이 커서 개방적이며 감각이 예민하고, 눈꼬리가 내려가 있어 느긋하며 자신의 속도로 일을 진행하는 성격을 보여줍니다. 코가 넓어 경제적 능력이 뛰어나고 외향적인 성격을 가지며, 입술이 얇아 신념이 강하고 자신의 생각을 고수하는 성격을 가지고 있습니다."
face_MBTI["ESTP"] = "미간이 좁아서 실용적이고 현실적인 사고를 중시하는 성격을 가지고 있습니다. 코가 짧아 낙천적이고 융통성이 있으며, 눈썹이 길어서 합리적이고 온화한 성격을 지니고 있습니다. 눈이 커서 감각이 예민하고 개방적인 성격을 나타내며, 눈꼬리가 내려가 있어 현재에 집중하고 느긋한 성격을 보여줍니다. 코가 넓어 외향적이고 경제적 능력이 뛰어나며, 입술이 두꺼워 추진력이 강하고 정열적인 성격을 가지고 있습니다."
face_MBTI["ESFP"] = "미간이 좁아 사교적이고 즉흥적인 성격을 가지고 있습니다. 코가 짧아 낙천적이며 타인과 쉽게 어울리며, 눈썹이 짧아 때때로 자기중심적일 수 있지만 다른 사람들과 잘 어울립니다. 눈이 커서 감각이 예민하고 감수성이 발달되어 있으며, 눈꼬리가 내려가 있어 현재를 즐기며 느긋한 성격을 나타냅니다. 코가 넓어 외향적이고 활발하며, 경제적인 면에서도 능력이 있습니다. 입술이 두꺼워 정열적이고 감정 표현이 풍부한 성격을 가지고 있습니다."
face_MBTI["ENFP"] = "미간이 차분하고 넓어서 창의적이고 자유로운 사고를 지향하는 성격을 가지고 있습니다. 코가 짧아 타인과 쉽게 어울리고 낙천적인 성향을 보이며, 눈썹이 짧아 때로는 자기중심적일 수 있지만 창의적이고 개방적인 사고를 합니다. 눈이 커서 감수성이 풍부하고 개방적이며 직관력이 뛰어난 성격을 나타냅니다. 눈꼬리가 올라가 있어 목표를 이루기 위해 열정적으로 노력하는 모습을 보이고, 코가 좁아 감수성이 예민하고 섬세한 성격을 가지고 있습니다. 입술이 두꺼워 강한 추진력과 열정적인 성격을 나타냅니다."
face_MBTI["ENTP"] = "미간이 좁아 창의적이고 논쟁을 즐기는 성격을 가지고 있습니다. 코가 길어 신중하며 깊이 있는 사고를 하고, 눈썹이 길어서 합리적이며 전략적인 사고를 지향합니다. 눈이 커서 개방적이고 감각이 예민한 성격을 나타내며, 눈꼬리가 올라가 있어 목표를 향한 열정과 의지가 강합니다. 코가 넓어 외향적이고 경제적 능력이 뛰어나며, 입술이 두꺼워 정열적이고 자신의 아이디어를 추진하는 능력이 뛰어난 성격을 가지고 있습니다."
face_MBTI["ESTJ"] = "미간이 차분하고 넓어서 실용적이고 조직적인 성격을 가지고 있습니다. 코가 길어 보수적이고 신중한 성향을 보이며, 눈썹이 길어서 합리적이고 온화한 성격을 지니고 있습니다. 눈이 작아 내성적이고 신중하며, 외부 자극에 민감하지 않습니다. 눈꼬리가 올라가 있어 목표를 이루기 위해 확고한 의지를 가지고 있으며, 코가 넓어 외향적이고 경제적 능력이 뛰어납니다. 입술이 얇아 신념이 강하고 확고한 성격을 보여줍니다."
face_MBTI["ESFJ"] = "미간이 차분하고 넓어서 사교적이며 타인에게 배려심이 깊은 성격을 가지고 있습니다. 코가 길어 신중하고 보수적인 성향을 지니며, 눈썹이 짧아 이기적인 면이 적고 타인을 잘 돌보는 성향이 있습니다. 눈이 작아 내성적이며 타인을 돌보는 성격을 나타내고, 눈꼬리가 내려가 있어 느긋하며 타인과의 관계에서 안정감을 추구합니다. 코가 넓어 외향적이고 현실적이며 경제적인 면에서 뛰어나며, 입술이 두꺼워 감정이 풍부하고 정열적인 성격을 가지고 있습니다."
face_MBTI["ENFJ"] = "미간이 차분하고 넓어서 타인에게 영감을 주고 리더십이 뛰어난 성격을 가지고 있습니다. 코가 길어 신중하며 자신의 신념을 지키고 타인을 이끄는 성향이 있습니다. 눈썹이 길어서 합리적이고 타인에게 이해심이 많으며, 눈이 커서 감수성이 풍부하고 개방적이며 직관력이 뛰어난 성격을 나타냅니다. 눈꼬리가 올라가 있어 목표를 향한 열정이 강하고 타인을 위해 헌신하는 모습을 보입니다. 코가 좁아 예민하고 섬세한 성격을 지니고 있으며, 입술이 두꺼워 강한 추진력과 정열적인 성격을 보여줍니다."
face_MBTI["ENTJ"] = "미간이 차분하고 넓어서 전략적이고 리더십이 강한 성격을 가지고 있습니다. 코가 길어서 보수적이고 신중하며 자기주장이 강한 성향을 나타내고, 눈썹이 길어 논리적이고 합리적인 성격을 지니고 있습니다. 눈이 커서 감각이 예민하며 목표를 향해 집중하는 성격을 보이며, 눈꼬리가 올라가 있어 목표를 이루기 위해 강한 의지를 보입니다. 코가 넓어 외향적이고 경제적 능력이 뛰어나며, 입술이 얇아 신념이 강하고 흔들리지 않는 성격을 가지고 있습니다."
face_MBTI["INTJ"] = "미간이 차분하고 넓어서 전략적이고 미래지향적인 성격을 가지고 있습니다. 코가 길어 신중하고 자기주장이 강한 성격을 나타내며, 눈썹이 길어서 논리적이고 계획적인 성격을 지녔습니다. 눈이 커서 분석력이 뛰어나고 신념이 확고하며, 눈꼬리가 올라가 있어 목표 달성에 강한 의지를 보입니다. 코가 넓어 외향적이고 실질적인 능력이 뛰어나며, 입술이 얇아 신념이 확고하고 흔들리지 않는 성격을 보여줍니다."
golen_ratio = {"미간": 56, "중안부": 132, "눈썹길이":106,
               "눈크기": 19, "눈꼬리":3,
               "코 넓이": 2627, "입술두께": 36}

def check():
    Migan = face_point[22][0] - face_point[21][0]
    if Migan > golen_ratio["미간"]:
        checking_list[0] = 1
    elif Migan < golen_ratio["미간"]:
        checking_list[0] = -1

    JungAnbu = face_point[32][1] - face_point[22][1]
    if JungAnbu > golen_ratio["중안부"]:
        checking_list[1] = 1
    elif JungAnbu < golen_ratio["중안부"]:
        checking_list[1] = -1

    NunSseopGil = face_point[26][0] - face_point[22][0]
    if NunSseopGil > golen_ratio["눈썹길이"]:
        checking_list[2] = 1
    elif NunSseopGil < golen_ratio["눈썹길이"]:
        checking_list[2] = -1

    NunKeokGi = face_point[43][1] - face_point[47][1]
    if NunKeokGi > golen_ratio["눈크기"]:
        checking_list[3] = 1
    elif NunKeokGi < golen_ratio["눈크기"]:
        checking_list[3] = -1

    NunKkori = face_point[42][1] - face_point[45][1]
    if NunKkori > golen_ratio["눈꼬리"]:
        checking_list[4] = 1
    elif NunKkori < golen_ratio["눈꼬리"]:
        checking_list[4] = -1

    KoNeolBi = face_point[35][0] - face_point[31][0]
    if KoNeolBi > golen_ratio["코 넓이"]:
        checking_list[5] = 1
    elif KoNeolBi < golen_ratio["코 넓이"]:
        checking_list[5] = -1

    IpSoolDukke = face_point[51][1] - face_point[57][1]
    if IpSoolDukke > golen_ratio["입술두께"]:
        checking_list[6] = 1
    elif IpSoolDukke < golen_ratio["입술두께"]:
        checking_list[6] = -1

def check_MBTI(features):
    max_similarity = -1
    best_match = None

    for mbti in MBTI:
        similarity = sum(1 for x, y in zip(MBTI[mbti], features) if x == y)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = mbti

    return best_match

def pick_random_subject(subject, mbti, num_elements=3):
    return random.sample(subject[mbti], num_elements)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

checking_list = [0] * 7
face_point = defaultdict(list)

# def analyze_face(image_path):
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     faces = detector(gray)

#     if len(faces) == 0:
#         return "얼굴을 인식하지 못했습니다.", []

#     for face in faces:
#         landmarks = predictor(gray, face)

#         for n in range(68):
#             x = landmarks.part(n).x
#             y = landmarks.part(n).y
#             face_point[n] = [x, y]

#         # 골든 레이시오 체크
#         check()

#     mbti_type = check_MBTI(checking_list)
#     return mbti_type, pick_random_subject(INHA, mbti_type)

def analyze_face(image_path, school):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        return "얼굴을 인식하지 못했습니다.", [], None

    for face in faces:
        landmarks = predictor(gray, face)

        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            face_point[n] = [x, y]

            # 랜드마크를 이미지에 표시
            cv2.circle(image, (x, y), 2, (255, 0, 0), -1)

        # 골든 레이시오 체크
        check()

    # school 인자에 따라 학과 추천 리스트를 선택
    if school == 'inha':
        subject_list = INHA
    elif school == 'sangmyung-seoul':
        subject_list = SEOUL
    elif school == 'sangmyung-cheonan':
        subject_list = CHEONAN
    else:
        return "잘못된 학교 선택입니다.", [], None

    # 랜드마크가 표시된 이미지 저장
    output_image_path = image_path.replace(".jpg", "_landmarks.jpg").replace(".png", "_landmarks.png")
    cv2.imwrite(output_image_path, image)

    mbti_type = check_MBTI(checking_list)
    
    return mbti_type, pick_random_subject(subject_list, mbti_type), output_image_path



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files or 'school' not in request.form:
            return redirect(request.url)

        file = request.files['file']
        school = request.form['school']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure the upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)

            mbti_type, recommended_subjects, landmarks_image_path = analyze_face(filepath, school)
            mbti_type = face_MBTI[mbti_type]
            recommended_subject = [{"name": item["name"], "url": item["url"]} for item in subjects if item["name"] in recommended_subjects]

            return render_template('result.html', mbti_type=mbti_type, subjects=recommended_subject, image_path=landmarks_image_path)

    return render_template('upload.html')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure the upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)

            mbti_type, recommended_subjects = analyze_face(filepath)
            mbti_type = face_MBTI[mbti_type]
            recommended_subject = [{"name": item["name"], "url": item["url"]} for item in subjects if item["name"] in recommended_subjects]
            return render_template('result.html', mbti_type=mbti_type, subjects=recommended_subject, image_path=filepath)

    return render_template('upload.html')

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)