
# WebAipのテスト版を作るひな形パッケージ


from socketutil.resp.response import Response
from socketutil.reqs.request import Request

from socketutil.myclient.my_scoket_client import MySocketClient
from socketutil.myserver.my_scoket_server import MySocketServer

__copyright__    = 'Copyright (C) 2024 HiddenUtility'
__version__      = '1000'
__license__      = 'BSD-3-Clause'
__author__       = 'HiddenUtility'
__author_email__ = 'i.will.be.able.to.see.you@gmail.com'
__url__          = 'https://github.com/HiddenUtility/pyutil'

__all__ = [
    'MySocketClient',
    'MySocketServer',
    'Response',
    'Request',

]