import os
from typing import List, Dict, Union
import chardet  # detectarea encoding-ului fisierelor

class GenericFile:
    def get_path(self) -> str:
        raise NotImplementedError("metoda get_path lipseste")

    def get_freq(self) -> int:
        raise NotImplementedError("metoda get_freq lipseste")

class TextASCII(GenericFile):
    def __init__(self, path_absolut: str, frecvente: int) -> None:
        self.path_absolut = path_absolut
        self.frecvente = frecvente

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> int:
        return self.frecvente

class XMLFile(TextASCII):
    def __init__(self, path_absolut: str, frecventa: int, first_tag: str) -> None:
        super().__init__(path_absolut, frecventa)
        self.first_tag = first_tag

    def get_first_tag(self) -> str:
        return self.first_tag

class TextUNICODE(GenericFile):
    def __init__(self, path_absolut: str, frecvente: int) -> None:
        self.path_absolut = path_absolut
        self.frecvente = frecvente

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> int:
        return self.frecvente

class Binary(GenericFile):
    def __init__(self, path_absolut: str, frecvente: int) -> None:
        self.path_absolut = path_absolut
        self.frecvente = frecvente

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> int:
        return self.frecvente

class BMP(Binary):
    def __init__(self, path_absolut: str, frecventa: int, width: int, height: int, bpp: int) -> None:
        super().__init__(path_absolut, frecventa)
        self.width = width
        self.height = height
        self.bpp = bpp

    def show_info(self) -> None:
        print("Width:{}\nHeight: {}\nBPP: {}\n".format(self.width, self.height, self.bpp))

def calc_frecvente(content: bytes):
    frecvente = {}
    for byte in content:
        frecvente[byte] = frecvente.get(byte, 0) + 1
    return frecvente

def is_printable_ascii(byte: int) -> bool:
    return (32 <= byte <= 126) or (byte in {9, 10, 13})  # spații, \t, \n, \r

def read_files_in_directory(directory: str) -> List[Union[TextASCII, TextUNICODE, Binary, XMLFile, BMP]]:
    result = [] # lista rez

    for root, _, files in os.walk(directory): # parcurg recursiv continutul
        for filename in files:
            filepath = os.path.join(root, filename) # cale fisier

            try:
                with open(filepath, 'rb') as f: # deschid fisierul in mod binar si-l citesc
                    content = f.read()

                frecvente = calc_frecvente(content)
                encoding = chardet.detect(content)['encoding']

                # BMP (primii 2 biti = 'BM')
                if content[:2] == b'BM':
                    width = int.from_bytes(content[18:22], 'little')
                    height = int.from_bytes(content[22:26], 'little')
                    bpp = int.from_bytes(content[28:30], 'little')
                    result.append(BMP(filepath, frecvente, width, height, bpp))
                    continue

                # XML (începe cu <?xml)
                if content.lstrip().startswith(b'<?xml'):
                    first_tag = content.split(b'>')[0] + b'>'
                    result.append(XMLFile(filepath, frecvente, first_tag.decode('ascii', errors='ignore')))
                    continue

                # fișiere text (ASCII/Unicode)
                try:
                    text_content = content.decode('utf-8') # standardul utf 8
                    printable_count = sum(is_printable_ascii(byte) for byte in content) # raport caractere printabile
                    ratio = printable_count / len(content) if content else 0

                    if encoding in ['UTF-16', 'UTF-16LE', 'UTF-16BE']: # UNICODE
                        result.append(TextUNICODE(filepath, frecvente))
                    elif ratio > 0.8:  # ASCII pt >80% caractere printabile
                        result.append(TextASCII(filepath, frecvente))
                    else: # Binary
                        result.append(Binary(filepath, frecvente))
                except UnicodeDecodeError:
                    result.append(Binary(filepath, frecvente))

            except (IOError, PermissionError):
                continue

    return result

if __name__ == "__main__":
    directory = input("PATH: ")
    print(" ")
    for it in read_files_in_directory(directory):
        if isinstance(it, BMP):
            print("BMP: {}, \nDimensiuni: ".format(it.get_path()))
            it.show_info()
        elif isinstance(it, XMLFile):
            print("XML: {}".format(it.get_path()))
        elif isinstance(it, TextUNICODE):
            print("UNICODE: {}".format(it.get_path()))
        elif isinstance(it, TextASCII):
            print("ASCII: {}".format(it.get_path()))
        elif isinstance(it, Binary):
            print("Binary: {}".format(it.get_path()))
        print()
