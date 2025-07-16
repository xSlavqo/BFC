# client/managers/ocr_manager.py
import easyocr
import numpy as np
from spellchecker import SpellChecker # <--- DODANY IMPORT

class OcrManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.spell = SpellChecker() # <--- INICJALIZACJA KOREKTORA
        try:
            self.reader = easyocr.Reader(['en'])
            self.logger.warning("Menedżer OCR zainicjowany z easyocr i korektorem pisowni.")
        except Exception as e:
            self.logger.error(f"Nie udało się zainicjować easyocr: {e}")
            self.reader = None

    def find_text_in_image(self, image, text_to_find):
        """
        Znajduje tekst w obrazie, używając korekty pisowni do naprawy błędów OCR.
        """
        if not self.reader:
            self.logger.error("Reader easyocr nie jest dostępny.")
            return None
        try:
            image_np = np.array(image)
            results = self.reader.readtext(image_np)
            
            # Zbierz wszystkie słowa rozpoznane przez OCR
            all_words = []
            for (_, text, _) in results:
                all_words.extend(text.lower().split())

            # Znajdź nieznane słowa i zaproponuj dla nich korekty
            unknown_words = self.spell.unknown(all_words)
            
            for (bbox, text, prob) in results:
                # Sprawdź, czy szukane słowo jest w oryginalnym tekście
                if text_to_find.lower() in text.lower():
                    return bbox
                
                # Sprawdź, czy szukane słowo jest korektą dla słowa z obrazu
                for word in text.lower().split():
                    if word in unknown_words:
                        correction = self.spell.correction(word)
                        if correction == text_to_find.lower():
                            return bbox
            return None
        except Exception as e:
            self.logger.error(f"Błąd podczas wyszukiwania tekstu w obrazie: {e}")
            return None

    def read_text_from_image_region(self, image, region):
        """
        Odczytuje cały tekst z określonego regionu podanego obrazu.
        """
        if not self.reader:
            self.logger.error("Reader easyocr nie jest dostępny.")
            return ""
        try:
            x, y, w, h = region
            cropped_image = np.array(image)[y:y+h, x:x+w]
            results = self.reader.readtext(cropped_image, detail=0, paragraph=True)
            return " ".join(results)
        except Exception as e:
            self.logger.error(f"Błąd podczas odczytu tekstu z regionu obrazu: {e}")
            return ""