# -*- coding: utf-8 -*-
"""houghTransform.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zMqZRynNUxSCh5QTeMIuAgZhwVj2VXph
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def display_image(title, image, cmap_type='gray'):
    plt.figure(figsize=(6, 6))
    if len(image.shape) == 3:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(image, cmap=cmap_type)
    plt.title(title)
    plt.axis('off')
    plt.show()

image= cv2.imread('/content/stock-photo-road-going-volcanic-area-lanzarote-island-canary-islands-spain.jpeg')
#cv use bgr color while the normal is rgb
#display_image('Original Image', image)

roadMedianFilter= cv2.medianBlur(image, 5)
#display_image('Road Median Filter', roadMedianFilter)

roadEdge= cv2.Canny(roadMedianFilter, 100, 150)
#display_image('Road Edge', roadEdge)

mask= np.zeros_like(roadEdge)

rows, cols = image.shape[:2]
bottom_left  = [cols * 0.09, rows * 0.95]
top_left     = [cols * 0.8, rows * 0.45]
bottom_right = [cols * 0.9, rows * 0.95]
top_right    = [cols * 0.8, rows * 1]

vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
cv2.fillPoly(mask, vertices, 255)
display_image('Mask', mask)

ROI= cv2.bitwise_and(roadEdge, mask)
display_image('Region of Interest', ROI)

# Hough transform for line detection
lines = cv2.HoughLinesP(ROI, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=50)
line_image = np.zeros_like(image)
if lines is not None:
  for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)

combined_image = cv2.addWeighted(image, 0.8, line_image, 1, 0)
display_image('Lane Detection with Hough Transform', combined_image)

import math

def hough_transform(edge_image, theta_res=1, rho_res=1):
    height, width = edge_image.shape
    max_dist = int(math.sqrt(height**2 + width**2))
    rhos = np.arange(-max_dist, max_dist, rho_res)
    thetas = np.deg2rad(np.arange(-90, 90, theta_res))

    accumulator = np.zeros((len(rhos), len(thetas)), dtype=np.int64)
    edge_points = np.argwhere(edge_image)

    for y, x in edge_points:
        for t_idx, theta in enumerate(thetas):
            rho = int(x * np.cos(theta) + y * np.sin(theta))
            rho_idx = np.argmin(np.abs(rhos - rho))
            accumulator[rho_idx, t_idx] += 1

    return accumulator, thetas, rhos

def detect_lines(accumulator, thetas, rhos, threshold):
    lines = []
    for rho_idx in range(accumulator.shape[0]):
        for theta_idx in range(accumulator.shape[1]):
            if accumulator[rho_idx, theta_idx] > threshold:
                rho = rhos[rho_idx]
                theta = thetas[theta_idx]
                lines.append((rho, theta))
    return lines

def draw_detected_lines(image, lines, mask, color=(0, 255, 0), thickness=2):
    for rho, theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        # Only draw the line if it falls within the ROI mask
        line_image = np.zeros_like(image)
        cv2.line(line_image, (x1, y1), (x2, y2), color, thickness)
        line_image = cv2.bitwise_and(line_image, line_image, mask=mask)
        image[np.where(line_image != 0)] = line_image[np.where(line_image != 0)]

accumulator, thetas, rhos = hough_transform(ROI)


line_threshold = 100
lines = detect_lines(accumulator, thetas, rhos, line_threshold)

lane_image = image.copy()
draw_detected_lines(lane_image, lines, mask)

display_image('Detected Lanes', lane_image)