# client/managers/ocr_manager.py
import easyocr
import numpy as np

class OcrManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        try:
            self.reader = easyocr.Reader(['en'])
            self.logger.warning("Menedżer OCR zainicjowany z easyocr.")
        except Exception as e:
            self.logger.critical(f"Nie udało się zainicjować easyocr: {e}")
            self.reader = None

    def find_text_in_image(self, image, text_to_find):
        """
        Znajduje określony tekst w podanym obrazie.
        """
        if not self.reader:
            self.logger.critical("Reader easyocr nie jest dostępny.")
            return None
        try:
            image_np = np.array(image)
            results = self.reader.readtext(image_np)
            for (bbox, text, prob) in results:
                if text_to_find.lower() in text.lower():
                    self.logger.info(f"Znaleziono tekst '{text_to_find}' z prawdopodobieństwem {prob:.2f}")
                    return bbox
            return None
        except Exception as e:
            self.logger.critical(f"Błąd podczas wyszukiwania tekstu w obrazie: {e}")
            return None

    def read_text_from_image_region(self, image, region):
        """
        Odczytuje cały tekst z określonego regionu podanego obrazu.
        """
        if not self.reader:
            self.logger.critical("Reader easyocr nie jest dostępny.")
            return ""
        try:
            x, y, w, h = region
            cropped_image = np.array(image)[y:y+h, x:x+w]
            results = self.reader.readtext(cropped_image, detail=0, paragraph=True)
            return " ".join(results)
        except Exception as e:
            self.logger.critical(f"Błąd podczas odczytu tekstu z regionu obrazu: {e}")
            return ""
