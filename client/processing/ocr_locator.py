# client/processing/ocr_locator.py
import warnings
import numpy as np
import easyocr
from spellchecker import SpellChecker

# Ignoruj konkretne ostrzeżenie z biblioteki torch, które jest generowane przez easyocr
# To najlepsze miejsce na ten kod, ponieważ problem powstaje właśnie tutaj.
warnings.filterwarnings("ignore", message=".*'pin_memory' argument is set as true.*")

class OcrLocator:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.spell_en = SpellChecker(language='en')

    def find_word_in_image(self, image, target_word):
        """
        Znajduje określone słowo na podanym obrazie PIL.
        Zwraca bounding box znalezionego słowa lub None.
        """
        target_word = target_word.lower()
        results = self.reader.readtext(np.array(image))
        
        for (bbox, text, prob) in results:
            found_word = text.lower()
            if found_word == target_word or self.spell_en.correction(found_word) == target_word:
                return bbox
        return None
