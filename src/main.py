# Script for detecting bubbles in a video stream with boiling water
import json
import cv2
import numpy as np
from bubble_tracker import BubbleTracker
from excel import DataTable
from dataclasses import asdict


LOL_VALUES = [10000, -10000, 5000, -5000]
cap = cv2.VideoCapture('bubbles.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
object_detector = cv2.createBackgroundSubtractorMOG2(history=100,
                                                     varThreshold=10)
# Write output to video file
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0,
                      (1080, 1920))

bubble_tracker = BubbleTracker()
data_table = DataTable('data.xlsx')
jason = {}

while True:
    ret, frame = cap.read()

    try:
        height, width, _ = frame.shape
    except AttributeError:
        break # Extract Region of interest
    roi = frame[0: 1600, 465: 563]
    coil_top = 780
    coil_bottom = 1060

    mask = object_detector.apply(roi)

    contrs, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                 cv2.CHAIN_APPROX_TC89_KCOS)

    big_bubble_parts = []
    small_bubbles = []
    top_y, bottom_y = 0, 10000
    big_bubble = False
    all_bubbles = []

    for cont in contrs:
        # check if pixel color in contour is white
        area = cv2.contourArea(cont)

        if area > 30:  # Sort out small noise
            x, y, w, h = cv2.boundingRect(cont)

            if w > 55 or h > 60:  # Big bubble parts only
                big_bubble_parts.append([x, y, w, h])
                # Так как y инвертирован, то максимальное значение y - это
                # минимальное значение y на экране
                top_y = min(top_y, y)
                bottom_y = max(bottom_y, y+h)
                continue

            # Малый пузырь не может быть ниже большого пузыря.
            # Если контур ниже, то это погрешность и это большой пузырь
            if big_bubble_parts != [] and y+h > bottom_y:
                min_y = y+h
                continue

            small_bubbles.append([x, y, w, h])

    minx, miny, maxx, maxy = 10000, 10000, 0, 0
    for x, y, w, h in big_bubble_parts:
        minx, miny, maxx, maxy = (min(minx, x), min(miny, y),
                                  max(maxx, x + w), max(maxy, y + h))

    big_bubble_final_width = maxx - minx
    big_bubble_final_height = maxy - miny
    if not big_bubble:
        if big_bubble_final_height > 200 and big_bubble_final_width > 40 \
           and maxy > coil_bottom:
            # get frame of bubble
            bubble = mask[miny:maxy, minx:maxx]
            # get average color of bubble
            avg_color = np.average(bubble)
            if avg_color > 100:
                cv2.rectangle(roi, (minx, miny), (maxx, maxy), (0, 100, 255),
                              2)
                big_bubble = True
                all_bubbles.append([minx, miny, big_bubble_final_width,
                                    big_bubble_final_height, True])
        else:
            if big_bubble_final_width in LOL_VALUES or \
               big_bubble_final_width in LOL_VALUES or miny in LOL_VALUES:
                continue
            # add this bubble to small bubbles (by miny)
            small_bubbles.append([minx, miny, big_bubble_final_width,
                                  big_bubble_final_height])
            all_bubbles.append([minx, miny, big_bubble_final_width,
                                big_bubble_final_height, False])

    for x, y, w, h in small_bubbles:
        # sort out strange noise
        if w in LOL_VALUES or h in LOL_VALUES or y in LOL_VALUES:
            continue
        # sort if small bubble is in big bubble
        if not big_bubble and y+h < coil_bottom and y < maxy:
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
            all_bubbles.append([x, y, w, h, False])

    data = bubble_tracker.update(all_bubbles)
    bubbles_to_table = []
    bubbles_to_json = []
    for d in data.values():
        # draw id on bubble
        cv2.putText(roi, str(d.id), (d.center[0], d.center[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        bubbles_to_table.append(d)
        bubbles_to_json.append(asdict(d))

    # pprint(bubble_tracker.bubbles)

    # get time
    time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    data_table.push(time, bubbles_to_table)
    if jason.get(time) is None:
        jason[time] = bubbles_to_json
    else:
        jason[time].append(bubbles_to_json)

    # cv2.imshow('Mask', mask)
    # cv2.imshow('Frame', frame)
    out.write(frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
out.release()
data_table.save()
json.dump(jason, open('data.json', 'w'))
cv2.destroyAllWindows()
