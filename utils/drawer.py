import cv2


def draw_rect(img, boxes, color=(255, 0, 0), box_thickness=2):
    if isinstance(boxes, list):
        for (x, y, w, h) in boxes:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, box_thickness)
    elif isinstance(boxes, tuple):
        x, y, w, h = boxes
        cv2.rectangle(img, (x, y), (x + w, y + h), color, box_thickness)
    return img
