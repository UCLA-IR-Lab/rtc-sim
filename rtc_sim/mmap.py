import mmap
import os

WORD_SIZE = 8
MAP_SIZE = 1024 * WORD_SIZE

class Mmap:
    def __init__(self, mmap_file) -> None:
        self._mmap_file = mmap_file
        self._mm = None
        if os.path.exists(self._mmap_file):
            self._create_mmap_file()
        else:
            self._create_mmap_file()
            self._read_mmap_file()
            
    def _create_mmap_file(self):
        with open(self._mmap_file, mode="wb") as file:
            initStr = '00' * MAP_SIZE
            initByte = bytes.fromhex(initStr)
            file.write(initByte)
            
    def _read_mmap_file(self):
        with open(self._mmap_file, mode="r+b") as file:
            self._mm = mmap.mmap(file.fileno(), 0)
            self._mm.seek(0)
            
    def read_short(self, adr: int):
        try:
            self._mm.seek(adr*WORD_SIZE)
            bytes = self._mm.read(WORD_SIZE)
            val = int.from_bytes(bytes, 'little', signed=True)
            self._mm.seek(0)
            return val
        except Exception as e:
            print("read_short except: " + str(e).replace('\n', ''))
            return
        
    def write_short(self, adr: int, data) -> None:
        if data >= (2**(8*WORD_SIZE)):
            print("Error: over 8 bytes")
            return
        
        try:
            ddata = int(data)
            bytes = ddata.to_bytes(WORD_SIZE, 'little', signed=True)
            for i in range(WORD_SIZE):
                self._mm[adr*WORD_SIZE + i] = bytes[i]
        except Exception as e:
            print("write_short except: " + str(e).replace('\n', ''))
            
    def close(self):
        self._mm.close()