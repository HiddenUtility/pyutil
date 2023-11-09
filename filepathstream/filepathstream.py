# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 08:53:13 2023

@author: nanik
"""
from __future__ import annotations
import abc
from pathlib import Path

import re
from datetime import datetime
import random


#interface
class Interface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_filepaths(self):
        raise NotImplementedError()
    @abc.abstractmethod
    def get_file_size(self):
        raise NotImplementedError()
    @abc.abstractmethod
    def sort(self)->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def narrow_down_datetime(self,start: datetime, end: datetime)->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def reduce_number(self)->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def reduce_rate(self)->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def drop_filenames(self,names: list[str])->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def drop_datetimes(self,datetimes: list[datetime])->FilepathListStream:
        raise NotImplementedError()
    @abc.abstractmethod
    def narrow_to_contain_keys(self,*key: str) -> FilepathListStream:
        raise NotImplementedError()
        
class FilepathListStream(Interface):
    __filepaths: list[Filepath]
    __empty: bool
    count: int
    def __init__(self,src:Path = None, glob="*", _filepaths:list[Filepath]=[]):
        self.__filepaths = _filepaths
        self.count = 0
        self.__empty = len(self.__filepaths) == 0
        if src is None:return
        if self.__filepaths:return
        if not src.is_dir(): ValueError(f"{src} is Not Directory Path")
        self.__filepaths = [Filepath(f) for f in src.glob(glob) if f.is_file()]
        self.__empty = len(self.__filepaths) == 0
        
    def _return(self,filepaths: list[Filepath]) -> FilepathListStream :
        return FilepathListStream(_filepaths=filepaths)
    
    def __str__(self):
        if len(self.__filepaths) <= 10:
            return "".join(["%s\n" % f for f in self.__filepaths])
        return "".join(["%s\n" % f for f in self.__filepaths[:10]])+"\n.\n.\n."
    def __repr__(self):
        return self.__str__()
    def __len__(self):
        return len(self.__filepaths)
    def __iter__(self):
        return self
    def __next__(self):
        if self.count == len(self.__filepaths):
            raise StopIteration
        self.count+=1
        return self.__filepaths[self.count - 1].get_filepath()
    
    def __add__(self, obj: FilepathListStream):
        if not isinstance(obj, FilepathListStream):raise TypeError
        filepaths = self.__filepaths + obj.filepaths
        self._return(list(set(filepaths)))
    
    @property
    def empty(self):
        return self.__empty

    #//Override
    def get_filepaths(self)->list[Path]:
        return [f.get_filepath() for f in self.__filepaths]
    #//Override
    def get_file_size(self,num=10) -> float:
        """
        Parameters
        ----------
        num : TYPE, optional
            randumでn個のデータを開いて平均値を求める。
            デフォルトは10個

        Returns
        -------
        float
            平均値を返す。（kbyte）
        """
        if len(self.__filepaths):return 0.0
        filepaths = self.__filepaths if len(self.__filepaths) < 10 else random.sample(self.__filepaths, num)
        sizes = [path.stat().st_size for path in filepaths]
        return sum(sizes) / len(sizes) //1000
    
    #@Override
    def sort(self, reverse=False) -> FilepathListStream:
        filepaths = sorted(self.__filepaths, reverse=reverse)
        return self._return(filepaths)
    #@Override
    def narrow_down_datetime(self,
                             start: datetime=datetime(2000, 1, 1),
                             end: datetime=datetime(2099,12,31)) -> FilepathListStream:
        if not isinstance(start, datetime): raise TypeError
        if not isinstance(end, datetime): raise TypeError
        if end < start: raise ValueError
        filepaths = [f for f in self.__filepaths if start < f < end]
        return self._return(filepaths)
        
    #@Override
    def reduce_number(self, n: int | None)->FilepathListStream:
        if n is None:return self
        if not isinstance(n, int): raise TypeError
        if len(self.__filepaths) <= n: return self
        filepaths = random.sample(self.__filepaths, n)
        return self._return(filepaths)
    #@Override
    def reduce_rate(self, r: float | None)->FilepathListStream:
        if r is None:return self
        if not (0 < r < 1):raise ValueError
        n = int(len(self.__filepaths) * r)
        return self.reduce_number(n)
    
    #@Override
    def drop_filenames(self,names: list[str]) -> FilepathListStream:
        if len(names) == 0:return self
        filepaths = [f for f in self.__filepaths if f.name not in names]
        return self._return(filepaths)
    #@Override
    def drop_datetimes(self,datetimes: list[datetime]) -> FilepathListStream:
        if len(datetimes) == 0:return self
        filepaths = [f for f in self.__filepaths if f._datetime not in datetimes]
        return self._return(filepaths)
    
    #@Override
    def narrow_to_contain_keys(self,*keys: str) -> FilepathListStream:
        filepaths = []
        for k in keys:
            filepaths += [f for f in self.__filepaths if k in f.name]
        return self._return(filepaths)

class Filepath:
    def __init__(self,f: Path):
        if not f.is_file():raise ValueError(f"{f}はfilepathではありません。")
        self.filepath = f
        self.name = f.name
        self._datetime = self._get_datetime(f.stem)
        self.suffix = f.suffix
    def _get_datetime(self, name: str) -> datetime:
        findings = re.findall("\d{14}",name)
        if len(findings) == 0:
            return datetime.timestamp(self.filepath.stat().st_ctime)
        for finding in findings:
            try:
                return datetime.strptime(finding.group(), '%Y%m%d%H%M%S') 
            except:
                pass
        raise HasNotDatetimeError(f"{name}はdatetime情報を持ちません。")
    
    def __eq__(self, o: datetime):
        return self._datetime == o
    def __ne__(self, o: datetime):
        return self._datetime != o
    def __lt__(self, o: datetime):
        return self._datetime < o
    def __le__(self, o: datetime):
        return self._datetime <= o
    def __gt__(self, o: datetime):
        return self._datetime > o
    def __ge__(self, o: datetime):
        return self._datetime >= o
    def __str__(self):
        return f"{self._datetime}: {self.filepath.parent.name}/{self.filepath.name}"
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return hash(self._datetime)
    def get_datetime(self):
        return self._datetime
    def get_filepath(self):
        return self.filepath
    

class HasNotDatetimeError(Exception):
    pass