# ClashBot Launcher с автоматической активацией venv
Set-Location "c:\Users\SpencerMSU\Documents\Новая папка\ClashBOfClashBot"

Write-Host "🔧 Активация виртуального окружения..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Set-Location "ClashBOfClashBot"

Write-Host "🚀 Запуск ClashBot..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow

try {
    python main.py
}
catch {
    Write-Host "❌ Ошибка запуска: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🛑 Бот остановлен. Нажмите любую клавишу для выхода..." -ForegroundColor Yellow
Read-Host