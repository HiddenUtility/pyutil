# 1. 環境構築
サーバー上で動かすことを想定しているため、仮想で切って実装する。

## 1.1. python 3.11.*インストール

"Add Python 3.11 to PATH"はチェックしてはいけません。
　

## 1.2.任意の場所に置く

カレントディレクトリを任意の場所へ移動する。

## 1.3.ディレクトリ内にpythonの仮想環境構築
プロンプトで下記を実行して下さい。 

```　
py -3.11 -m venv .venv
```

## 1.4.仮想環境起動

続いて下記のコマンドを実行して下さい。
```
.venv\Scripts\activate
```

## 1.5. ライブラリインストール
### 1.5.1. オンラインの場合
```
pip install -r requirements.txt
```

### 1.5.2. オフラインの場合
```
pip install --no-index --find-link=libs wheel
pip install --no-index --find-link=libs -r requirements.txt
```
インストールが終了したら、libsとrequirements.txtは削除可能です。

