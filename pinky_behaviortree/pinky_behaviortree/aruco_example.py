import cv2
import numpy as np
import cv2.aruco as aruco

# 웹캠 초기화
cap = cv2.VideoCapture(0)

# 카메라 파라미터 (예시값, 실제 웹캠에 맞게 조정 필요)
camera_matrix = np.array([[800, 0, 320],
                         [0, 800, 240],
                         [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5,1), dtype=np.float32)

# ArUco 설정
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters_create()

# 마커 크기 (미터 단위, 실제 출력한 마커 크기에 맞게 조정 필요)
marker_size = 0.05  # 5cm = 0.05m

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        # 마커 검출 시각화
        aruco.drawDetectedMarkers(frame, corners, ids)
        
        # 각 마커의 포즈 추정
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)
        
        for i in range(len(ids)):
            # 좌표축 그리기
            aruco.drawAxis(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.03)
            
            # 회전 벡터를 오일러 각도로 변환
            rot_matrix, _ = cv2.Rodrigues(rvecs[i])
            euler_angles = cv2.RQDecomp3x3(rot_matrix)[0]
            
            # 거리 계산 (tvecs의 norm)
            distance = np.sqrt(tvecs[i][0][0]**2 + tvecs[i][0][1]**2 + tvecs[i][0][2]**2)
            
            # 정보 표시
            text_position = (10, 30 * (i + 1))
            cv2.putText(frame, f'Marker {ids[i][0]}:', (10, 30 * (i + 1)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'Distance: {distance:.2f}m', (10, 30 * (i + 2)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'Roll: {np.rad2deg(euler_angles[0]):.1f}deg', (10, 30 * (i + 3)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'Pitch: {np.rad2deg(euler_angles[1]):.1f}deg', (10, 30 * (i + 4)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'Yaw: {np.rad2deg(euler_angles[2]):.1f}deg', (10, 30 * (i + 5)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow('ArUco Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()