#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text segmentation utility functions.
"""
import numpy as np
# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Third-party modules
import pytesseract
from PIL import Image
import cv2


# ----------------------------------------------------------------------------
# Text segmentation_utility functions
# ----------------------------------------------------------------------------


class Text:
    def __init__(self, id, content, location):
        self.id = id
        self.content = content
        self.location = location

        self.width = self.location["right"] - self.location["left"]
        self.height = self.location["bottom"] - self.location["top"]
        self.area = self.width * self.height
        self.word_width = self.width / len(self.content)

    def visualize_element(self, img, color, line, show=False):
        loc = self.location
        cv2.rectangle(
            img,
            (loc["left"], loc["top"]),
            (loc["right"], loc["bottom"]),
            color,
            line,
        )
        if show:
            cv2.imshow("text", img)
            cv2.waitKey()
            cv2.destroyWindow("text")

    def is_justified(self, ele_b, direction='h', max_bias_justify=4):
        """
        Check if the element is justified
        :param ele_b:
        :param max_bias_justify: maximum bias if two elements to be justified
        :param direction:
             - 'v': vertical up-down connection
             - 'h': horizontal left-right connection
        """
        l_a = self.location
        l_b = ele_b.location
        # connected vertically - up and below
        if direction == 'v':
            # left and right should be justified
            if abs(l_a['left'] - l_b['left']) < max_bias_justify and abs(l_a['right'] - l_b['right']) < max_bias_justify:
                return True
            return False
        elif direction == 'h':
            # top and bottom should be justified
            if abs(l_a['top'] - l_b['top']) < max_bias_justify and abs(l_a['bottom'] - l_b['bottom']) < max_bias_justify:
                return True
            return False

    def is_on_same_line(self, text_b, direction='h', bias_gap=4, bias_justify=4):
        """
        Check if the element is on the same row(direction='h') or column(direction='v') with ele_b
        :param bias_justify:
        :param bias_gap:
        :param text_b:
        :param direction:
             - 'v': vertical up-down connection
             - 'h': horizontal left-right connection
        :return:
        """
        l_a = self.location
        l_b = text_b.location
        # connected vertically - up and below
        if direction == 'v':
            # left and right should be justified
            if self.is_justified(text_b, direction='v', max_bias_justify=bias_justify):
                # top and bottom should be connected (small gap)
                if abs(l_a['bottom'] - l_b['top']) < bias_gap or abs(l_a['top'] - l_b['bottom']) < bias_gap:
                    return True
            return False
        elif direction == 'h':
            # top and bottom should be justified
            if self.is_justified(text_b, direction='h', max_bias_justify=bias_justify):
                # top and bottom should be connected (small gap)
                if abs(l_a['right'] - l_b['left']) < bias_gap or abs(l_a['left'] - l_b['right']) < bias_gap:
                    return True
            return False

    def is_intersected(self, text_b, bias):
        l_a = self.location
        l_b = text_b.location
        left_in = max(l_a['left'], l_b['left']) + bias
        top_in = max(l_a['top'], l_b['top']) + bias
        right_in = min(l_a['right'], l_b['right'])
        bottom_in = min(l_a['bottom'], l_b['bottom'])

        w_in = max(0, right_in - left_in)
        h_in = max(0, bottom_in - top_in)
        area_in = w_in * h_in
        if area_in > 0:
            return True

    def merge_text(self, text_b):
        text_a = self
        top = min(text_a.location['top'], text_b.location['top'])
        left = min(text_a.location['left'], text_b.location['left'])
        right = max(text_a.location['right'], text_b.location['right'])
        bottom = max(text_a.location['bottom'], text_b.location['bottom'])
        self.location = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']
        self.area = self.width * self.height

        left_element = text_a
        right_element = text_b
        if text_a.location['left'] > text_b.location['left']:
            left_element = text_b
            right_element = text_a
        self.content = left_element.content + ' ' + right_element.content
        self.word_width = self.width / len(self.content)

    def shrink_bound(self, binary_map):
        bin_clip = binary_map[self.location['top']:self.location['bottom'], self.location['left']:self.location['right']]
        height, width = np.shape(bin_clip)

        shrink_top = 0
        shrink_bottom = 0
        for i in range(height):
            # top
            if shrink_top == 0:
                if sum(bin_clip[i]) == 0:
                    shrink_top = 1
                else:
                    shrink_top = -1
            elif shrink_top == 1:
                if sum(bin_clip[i]) != 0:
                    self.location['top'] += i
                    shrink_top = -1
            # bottom
            if shrink_bottom == 0:
                if sum(bin_clip[height-i-1]) == 0:
                    shrink_bottom = 1
                else:
                    shrink_bottom = -1
            elif shrink_bottom == 1:
                if sum(bin_clip[height-i-1]) != 0:
                    self.location['bottom'] -= i
                    shrink_bottom = -1

            if shrink_top == -1 and shrink_bottom == -1:
                break

        shrink_left = 0
        shrink_right = 0
        for j in range(width):
            # left
            if shrink_left == 0:
                if sum(bin_clip[:, j]) == 0:
                    shrink_left = 1
                else:
                    shrink_left = -1
            elif shrink_left == 1:
                if sum(bin_clip[:, j]) != 0:
                    self.location['left'] += j
                    shrink_left = -1
            # right
            if shrink_right == 0:
                if sum(bin_clip[:, width-j-1]) == 0:
                    shrink_right = 1
                else:
                    shrink_right = -1
            elif shrink_right == 1:
                if sum(bin_clip[:, width-j-1]) != 0:
                    self.location['right'] -= j
                    shrink_right = -1

            if shrink_left == -1 and shrink_right == -1:
                break
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']
        self.area = self.width * self.height
        self.word_width = self.width / len(self.content)


def visualize_texts(
        org_img, texts, color=(0, 0, 255), line=2, show=False, write_path=None
):
    img = org_img.copy()
    for text in texts:
        text.visualize_element(img, color=color, line=line)

    if show:
        cv2.imshow("Texts", img)
        cv2.waitKey(0)
        cv2.destroyWindow("Texts")

    if write_path is not None:
        cv2.imwrite(write_path, img)


def text2json(texts, img_shape):
    output = {"img_shape": img_shape, "texts": []}
    for text in texts:
        c = {"id": text.id, "content": text.content}
        loc = text.location
        c["column_min"], c["row_min"], c["column_max"], c["row_max"] = (
            loc["left"],
            loc["top"],
            loc["right"],
            loc["bottom"],
        )
        c["width"] = text.width
        c["height"] = text.height
        output["texts"].append(c)
    return output


def text_cvt_orc_format_tesseract(img: Image.Image):
    # Obtain bounding box information along with the OCR'd text
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    texts = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        if data['text'][i].strip():  # Ensure there's actual text
            location = {
                "left": data['left'][i],
                "top": data['top'][i],
                "right": data['left'][i] + data['width'][i],
                "bottom": data['top'][i] + data['height'][i],
            }
            content = data['text'][i]
            texts.append(Text(i, content, location))
    return texts


def merge_intersected_texts(texts):
    '''
    Merge intersected texts (sentences or words)
    '''
    changed = True
    while changed:
        changed = False
        temp_set = []
        for text_a in texts:
            merged = False
            for text_b in temp_set:
                if text_a.is_intersected(text_b, bias=2):
                    text_b.merge_text(text_a)
                    merged = True
                    changed = True
                    break
            if not merged:
                temp_set.append(text_a)
        texts = temp_set.copy()
    return texts


def text_filter_noise(texts):
    valid_texts = []
    for text in texts:
        if len(text.content) <= 1 and text.content.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&', '+']:
            continue
        valid_texts.append(text)
    return valid_texts


def text_sentences_recognition(texts):
    """
    Merge separate words detected by Google ocr into a sentence
    """
    changed = True
    while changed:
        changed = False
        temp_set = []
        for text_a in texts:
            merged = False
            for text_b in temp_set:
                if text_a.is_on_same_line(text_b, 'h', bias_justify=0.2 * min(text_a.height, text_b.height), bias_gap=2 * max(text_a.word_width, text_b.word_width)):
                    text_b.merge_text(text_a)
                    merged = True
                    changed = True
                    break
            if not merged:
                temp_set.append(text_a)
        texts = temp_set.copy()

    for i, text in enumerate(texts):
        text.id = i
    return texts