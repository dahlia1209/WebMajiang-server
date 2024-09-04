# PowerShellスクリプト: 麻雀ゲームプロジェクトのディレクトリ構造作成

# プロジェクトのルートディレクトリ名を設定
$projectName = "WebMajiang-server"

# ルートディレクトリを作成
New-Item -ItemType Directory -Force -Path $projectName

# ディレクトリ構造を作成する関数
function Create-Directory {
    param (
        [string]$path
    )
    New-Item -ItemType Directory -Force -Path "$projectName\$path"
}

# ファイルを作成する関数
function Create-File {
    param (
        [string]$path
    )
    New-Item -ItemType File -Force -Path "$projectName\$path"
}

# ディレクトリ構造の作成
Create-Directory "app"
Create-Directory "app\api\routes"
Create-Directory "app\api\websockets"
Create-Directory "app\core"
Create-Directory "app\db"
Create-Directory "app\models"
Create-Directory "app\schemas"
Create-Directory "app\services"
Create-Directory "app\utils"
Create-Directory "tests"
Create-Directory "tests\test_api"
Create-Directory "tests\test_models"
Create-Directory "tests\test_services"
Create-Directory "alembic\versions"

# ファイルの作成
Create-File "app\__init__.py"
Create-File "app\main.py"
Create-File "app\api\__init__.py"
Create-File "app\api\routes\__init__.py"
Create-File "app\api\routes\game.py"
Create-File "app\api\routes\player.py"
Create-File "app\api\websockets\__init__.py"
Create-File "app\api\websockets\game_socket.py"
Create-File "app\core\__init__.py"
Create-File "app\core\config.py"
Create-File "app\core\security.py"
Create-File "app\db\__init__.py"
Create-File "app\db\database.py"
Create-File "app\models\__init__.py"
Create-File "app\models\game.py"
Create-File "app\models\player.py"
Create-File "app\models\pai.py"
Create-File "app\schemas\__init__.py"
Create-File "app\schemas\game.py"
Create-File "app\schemas\player.py"
Create-File "app\services\__init__.py"
Create-File "app\services\game_service.py"
Create-File "app\services\player_service.py"
Create-File "app\utils\__init__.py"
Create-File "app\utils\helpers.py"
Create-File "tests\__init__.py"
Create-File "tests\conftest.py"
Create-File "tests\test_api\__init__.py"
Create-File "tests\test_api\test_game_routes.py"
Create-File "tests\test_api\test_player_routes.py"
Create-File "tests\test_models\__init__.py"
Create-File "tests\test_models\test_game.py"
Create-File "tests\test_models\test_player.py"
Create-File "tests\test_models\test_pai.py"
Create-File "tests\test_services\__init__.py"
Create-File "tests\test_services\test_game_service.py"
Create-File "tests\test_services\test_player_service.py"
Create-File ".env"
Create-File ".gitignore"
Create-File "requirements.txt"
Create-File "README.md"
Create-File "docker-compose.yml"

Write-Host "Project structure for $projectName has been created successfully!"