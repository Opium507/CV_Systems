import cv2
import numpy as np

def order_points(pts):
    """Упорядочивает координаты: верх-лево, верх-право, низ-право, низ-лево"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def process_image(base_img_path, slide_img_path, output_path):
    base = cv2.imread(base_img_path)
    slide = cv2.imread(slide_img_path)
    if base is None or slide is None:
        print("Ошибка загрузки изображений.")
        return

    # Поиск границ экрана
    gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Морфологическое замыкание для устранения разрывов
    kernel = np.ones((5, 5), np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(edges_closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    screen_contour = None
    for cnt in contours:
        if cv2.contourArea(cnt) < 5000:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        if len(approx) == 4:
            screen_contour = approx.reshape(4, 2)
            break
            
    if screen_contour is None:
        print("Экран не найден!")
        return
        
    dst_points = order_points(screen_contour)
    
    # Расчет гомографии и трансформация слайда
    h, w = slide.shape[:2]
    src_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    H, _ = cv2.findHomography(src_points, dst_points)
    warped_slide = cv2.warpPerspective(slide, H, (base.shape[1], base.shape[0]))
    
    # Создание маски для бесшовного наложения
    mask = np.zeros(base.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, dst_points.astype(int), 255)
    mask_inv = cv2.bitwise_not(mask)
    
    # Вырезаем "дырку" на месте экрана и вставляем искаженный слайд
    base_bg = cv2.bitwise_and(base, base, mask=mask_inv)
    slide_fg = cv2.bitwise_and(warped_slide, warped_slide, mask=mask)
    result = cv2.add(base_bg, slide_fg)
    
    cv2.imwrite(output_path, result)
    print(f"Готово! Результат сохранен в {output_path}")

# Запуск: можно заменить на свои изображения для тестирования
process_image("data/tv1.jpg", "data/slide.png", "results/result_photo.jpg")
process_image("data/test.png", "data/slide.png", "results/result_photo_test.jpg")
