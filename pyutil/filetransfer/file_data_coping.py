from pathlib import Path
import hashlib
import shutil
import time
from traceback import print_exc
from pyutil.filetransfer.error.CopyRetryCountOverError import CopyRetryCountOverError
from pyutil.filetransfer.error.DestinationSameFileExistsError import DestinationSameFileExistsError
from pyutil.filetransfer.error.DestinationSmallSizeFileError import DestinationSmallSizeFileError
from pyutil.filetransfer.error.DestinationUnknownFileError import DestinationUnknownFileError
from pyutil.filetransfer.error.FileMoveError import FileMoveError
from pyutil.filetransfer.file_data_remover import FileSourceDataRemover

class FileDataCoping:
    XXX = '.xxx'
    RETRY_COUNT = 3
    DERAY = 1
    __src : Path
    __dst : Path
    __dst_xxx : Path
    __is_removing : bool

    def __init__(self, src: Path, dst: Path,remove=True):
        if not isinstance(src, Path):
            raise TypeError()
        if not isinstance(dst, Path):
            raise TypeError()
        if not src.exists():
            raise FileNotFoundError()
        if not dst.exists():
            raise NotADirectoryError()
        
        self.__src: Path = src
        self.__dst: Path = dst / src.name
        self.__dst_xxx: Path = self.__dst.with_suffix(self.XXX)
        self.__is_removing = remove

        
    def __retry(self,func, *args, **kwargs):
        for i in range(self.RETRY_COUNT):
            try:
                func(*args, **kwargs)
                return
            except FileMoveError:
                time.sleep(self.DERAY)
            except Exception as e:
                raise e
        raise CopyRetryCountOverError(f"{func.__name__} {self.__src}をリトライしましたがうまく実行できました。")
    
    def __remove_dst(self):
        if self.__dst_xxx.exists():
            self.__dst_xxx.unlink()
        if self.__dst.exists():
            self.__dst.unlink()
    
    def __get_hash(self,filepath):
        with open(filepath,"rb") as f:
            body = f.read()
            hash_ = hashlib.sha256(body).hexdigest()
        return hash_
    
    def __is_same_hash(self) -> bool:
        return self.__get_hash(self.__src) == self.__get_hash(self.__dst)
    
    def __is_same_hash_xxx(self) -> bool:
        return self.__get_hash(self.__src) == self.__get_hash(self.__dst_xxx)
    
    def __is_small(self) -> bool:
        return self.__src.stat().st_size < self.__dst.stat().st_size
    
    def __copy(self):

        if self.__dst_xxx.exists():
            self.__dst_xxx.unlink()

        if self.__dst.exists():
            if self.__is_same_hash():
                if self.__is_removing: FileSourceDataRemover(self.__src).run()
                raise DestinationSameFileExistsError(f"{self.__dst}に既に同じファイルが存在します。")
            if self.__is_small():
                if self.__is_removing: FileSourceDataRemover(self.__src).run()
                raise DestinationSmallSizeFileError(f"{self.__dst}よりもファイルサイズが小さいです。")
            if self.__is_removing: FileSourceDataRemover(self.__src).run()
            raise DestinationUnknownFileError(f"{self.__dst}ソースと異なる不明なファイルが存在します。")
            

        try:
            shutil.copy2(self.__src, self.__dst_xxx)
        except Exception:
            print_exc()
            self.__remove_dst()
            raise FileMoveError()
            
        if not self.__is_same_hash_xxx():
            self.__remove_dst()
            raise FileMoveError()
        
        self.__dst_xxx.rename(self.__dst)
        
    def run(self):
        self.__retry(self.__copy)


