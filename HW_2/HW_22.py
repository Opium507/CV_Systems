import cv2
import numpy as np

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]
    return rect

def process_video_smooth(video_path, slide_img_path, output_path):
    cap = cv2.VideoCapture(video_path)
    slide = cv2.imread(slide_img_path)
    if not cap.isOpened() or slide is None:
        print("Ошибка загрузки данных.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    h_s, w_s = slide.shape[:2]
    src_points = np.array([[0, 0], [w_s, 0], [w_s, h_s], [0, h_s]], dtype=np.float32)
    
    last_dst_points = None
    alpha = 0.5  # Коэффициент сглаживания (0.0 - нет обновлений, 1.0 - нет сглаживания)

    while True:
        ret, frame = cap.read()
        if not ret: break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Наборы настроек: от строгих к мягким
        scenarios = [
            {"blur": (5, 5), "canny": (50, 150), "close": (5, 5)}, # Для монитора
            {"blur": (7, 7), "canny": (30, 100), "close": (9, 9)}, # Для черного ноутбука
        ]
        
        screen_contour = None
        for s in scenarios:
            blur = cv2.GaussianBlur(gray, s["blur"], 0)
            edges = cv2.Canny(blur, s["canny"][0], s["canny"][1])
            
            kernel = np.ones(s["close"], np.uint8)
            edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(edges_closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            for cnt in contours:
                if cv2.contourArea(cnt) < 5000: continue
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4:
                    screen_contour = approx.reshape(4, 2)
                    break # Нашли экран!
            
            if screen_contour is not None:
                break # Выходим из перебора сценариев, если экран найден
                
        # --- Блок сглаживания и наложения (остается без изменений) ---
        if screen_contour is not None:
            current_points = order_points(screen_contour)
            if last_dst_points is None:
                dst_points = current_points
            else:
                dst_points = (1 - alpha) * last_dst_points + alpha * current_points
            last_dst_points = dst_points
        else:
            dst_points = last_dst_points
            
        if dst_points is not None:
            H, _ = cv2.findHomography(src_points, dst_points)
            warped = cv2.warpPerspective(slide, H, (width, height))
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillConvexPoly(mask, dst_points.astype(int), 255)
            mask_inv = cv2.bitwise_not(mask)
            
            frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
            slide_fg = cv2.bitwise_and(warped, warped, mask=mask)
            frame = cv2.add(frame_bg, slide_fg)
            
        out.write(frame)

    cap.release()
    out.release()
    print(f"Готово! Видео сохранено в {output_path}")

# Запуск: можно заменить на свои видео и слайды для тестирования
process_video_smooth("data/IMG_8175.MOV", "data/slide.png", "results/result_video.mp4")
process_video_smooth("data/video.mp4", "data/slide.png", "results/result_video_test.mp4")