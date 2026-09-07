# coding=UTF-8
#
#   File        :   ocr.py
#
#   Author      :   GeeHB
#
#   Description :   ocr functions
#

import cv2
import pytesseract
from pytesseract import Output

#
#   OCR
#

# Parse an image file
#
def gridFromImage(self, fileName:str | None, removeFrames:bool=False, genBoxes:bool=False) -> bool:
    if fileName is None:
        return False

    img = cv2.imread(fileName)
    if img is not None:
        if removeFrames:
            img = self._removeFrames(img)
            if img is None:
                return False

        # Theorical dims of a rectangle
        dims = img.shape
        boxHeight = dims[0] / 9
        boxWidth = dims[1] / 9

        data = pytesseract.image_to_data(
            img, output_type=Output.DICT, config=TESSERACT_CONFIG
        )
        position = pointer(gameMode=False)

        for i in range(len(data["text"])):
            if data["conf"][i] != -1:
                # Coordinates
                x, y = data["left"][i], data["top"][i]
                w, h = data["width"][i], data["height"][i]

                line = (int)(y / boxHeight)
                row = (int)(x / boxWidth)

                text = data["text"][i]
                tLen = len(text)

                sWidth = (int)(w / tLen)
                top_left = (x, y)

                for index in range(tLen):
                    value = text[index]
                    position.moveTo(line, index + row)
                    self._setAt(
                        position, ord(value) - ord("0"), False
                    )  # Try to set the value in the grid

                    bottom_right = (top_left[0] + sWidth, top_left[1] + h)

                    if genBoxes:
                        cv2.rectangle(
                            img,
                            top_left,
                            bottom_right,
                            TESSERACT_BOX_COLOR,
                            TESSERACT_BOX_THICKNESS,
                        )

                    top_left = (bottom_right[0], top_left[1])

        if genBoxes:
            # Save the image with boxes
            full = os.path.splitext(fileName)
            dst = os.path.join(full[0] + "_boxes")
            dst += full[1]
            cv2.imwrite(dst, img)

        return True

    return False

# Remove vertical and horizontal frames around the grid
#
def _removeFrames(self, img):
    result = img.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    remove_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
    )
    cnts = cv2.findContours(
        remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cnts = cv2.findContours(
        remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

    return result
