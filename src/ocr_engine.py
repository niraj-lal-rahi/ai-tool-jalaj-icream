from __future__ import annotations

from typing import List


class OcrEngine:
    def __init__(self, languages: list[str] | None = None) -> None:
        self.languages = languages or ["en", "hi"]

        try:
            import easyocr  # type: ignore
            import cv2  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "OCR dependencies are missing. Install requirements.txt to run OCR pipeline."
            ) from exc

        self._easyocr = easyocr
        self._cv2 = cv2
        self.reader = easyocr.Reader(self.languages, gpu=False)

    def _preprocess(self, image_path: str):
        image = self._cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
        denoised = self._cv2.fastNlMeansDenoising(gray, h=20)
        thresholded = self._cv2.adaptiveThreshold(
            denoised,
            255,
            self._cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            self._cv2.THRESH_BINARY,
            31,
            2,
        )
        return thresholded

    def extract_lines(self, image_path: str) -> List[str]:
        img = self._preprocess(image_path)
        results = self.reader.readtext(img, detail=0, paragraph=False)

        return [str(item).strip() for item in results if str(item).strip()]
