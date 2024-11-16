## アプリケーション起動
cd C:\src\WebMajiang-server
.\env\Scripts\Activate.ps1
uvicorn app.main:app --reload

## テスト
cd C:\src\WebMajiang-server\tests
pytest -v