import dlib
import cv2

def analyze_face(image_path):
    # dlib의 얼굴 인식기 초기화
    detector = dlib.get_frontal_face_detector()
    image = cv2.imread(image_path)
    
    # 얼굴 인식
    faces = detector(image, 1)
    
    if len(faces) == 0:
        return "얼굴을 인식하지 못했습니다."
    
    # 얼굴이 인식되면 간단히 분석하여 학과를 추천
    face = faces[0]
    
    # 이 부분에서 얼굴 특성에 따라 학과를 결정하는 로직을 구현
    # 예시로 간단히 얼굴의 좌표로 학과를 임의로 추천
    if face.left() < 100:
        return "컴퓨터공학과"
    elif face.left() < 200:
        return "경영학과"
    else:
        return "예술학과"
