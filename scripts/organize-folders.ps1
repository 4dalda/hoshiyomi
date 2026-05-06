# ============================================================
#  フォルダ整理スクリプト
#  対象: ダウンロード / デスクトップ / ドキュメント
#  整理: ファイル種類別 → 日付（年月）別
# ============================================================

param(
    [switch]$DryRun   # -DryRun をつけると移動せずプレビューのみ
)

# ---- 設定 --------------------------------------------------

$TargetFolders = @(
    [Environment]::GetFolderPath("UserProfile") + "\Downloads",
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("MyDocuments")
)

$CategoryMap = @{
    "画像"             = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
                           ".heic", ".heif", ".raw", ".tiff", ".tif", ".ico")
    "動画"             = @(".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".m4v",
                           ".webm", ".ts", ".mts", ".3gp")
    "音楽"             = @(".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma",
                           ".opus", ".mid", ".midi")
    "文書"             = @(".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                           ".txt", ".rtf", ".odt", ".ods", ".odp", ".pages",
                           ".numbers", ".key", ".md", ".epub")
    "圧縮ファイル"     = @(".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz",
                           ".lzh", ".cab", ".iso")
    "プログラム"       = @(".exe", ".msi", ".msix", ".appx", ".bat", ".cmd", ".ps1")
    "コード"           = @(".py", ".js", ".ts", ".html", ".css", ".java", ".cpp",
                           ".c", ".cs", ".go", ".rs", ".rb", ".php", ".swift",
                           ".kt", ".json", ".xml", ".yaml", ".yml", ".toml",
                           ".ini", ".env", ".sh", ".sql", ".r", ".m", ".ipynb")
    "ショートカット"   = @(".lnk", ".url")
    "画像_RAWデータ"   = @(".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng")
}

# ---- ログ設定 -----------------------------------------------

$LogDir  = "$env:USERPROFILE\Documents\FolderOrganizer"
$LogFile = "$LogDir\organize_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line -ForegroundColor $Color
    if (-not $DryRun) {
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
    }
}

# ---- ユーティリティ -----------------------------------------

function Get-Category([string]$Extension) {
    $ext = $Extension.ToLower()
    foreach ($cat in $CategoryMap.Keys) {
        if ($CategoryMap[$cat] -contains $ext) { return $cat }
    }
    return "その他"
}

function Get-UniqueDestPath([string]$DestPath) {
    if (-not (Test-Path $DestPath)) { return $DestPath }
    $dir  = Split-Path $DestPath -Parent
    $base = [System.IO.Path]::GetFileNameWithoutExtension($DestPath)
    $ext  = [System.IO.Path]::GetExtension($DestPath)
    $i    = 2
    do {
        $newPath = Join-Path $dir "${base}_($i)${ext}"
        $i++
    } while (Test-Path $newPath)
    return $newPath
}

function Organize-Folder([string]$FolderPath) {
    if (-not (Test-Path $FolderPath)) {
        Write-Log "スキップ（フォルダが見つかりません）: $FolderPath" "DarkGray"
        return
    }

    $folderName = Split-Path $FolderPath -Leaf
    Write-Log ""
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"
    Write-Log "  整理開始: $folderName" "Cyan"
    Write-Log "  パス    : $FolderPath" "DarkGray"
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Cyan"

    # フォルダ直下のファイルのみ対象（サブフォルダは再帰しない）
    $files = Get-ChildItem -Path $FolderPath -File -ErrorAction SilentlyContinue

    $moved   = 0
    $skipped = 0

    foreach ($file in $files) {
        # システムファイル・隠しファイルはスキップ
        if ($file.Attributes -band [System.IO.FileAttributes]::System)  { $skipped++; continue }
        if ($file.Attributes -band [System.IO.FileAttributes]::Hidden)  { $skipped++; continue }
        # desktop.ini など Windows 管理ファイルはスキップ
        if ($file.Name -in @("desktop.ini", "thumbs.db", ".DS_Store"))  { $skipped++; continue }

        $category  = Get-Category $file.Extension
        $yearMonth = $file.LastWriteTime.ToString("yyyy-MM")

        $destDir  = Join-Path $FolderPath "$category\$yearMonth"
        $destPath = Get-UniqueDestPath (Join-Path $destDir $file.Name)

        $label = "$($file.Name)  →  $category\$yearMonth\"

        if ($DryRun) {
            Write-Log "  [プレビュー] $label" "Yellow"
        } else {
            try {
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Move-Item -Path $file.FullName -Destination $destPath -ErrorAction Stop
                Write-Log "  [移動完了]  $label" "Green"
                $moved++
            } catch {
                Write-Log "  [エラー]    $($file.Name) : $_" "Red"
                $skipped++
            }
        }
    }

    if ($DryRun) {
        Write-Log "  → プレビュー完了（実際の移動はなし）" "Yellow"
    } else {
        Write-Log "  → 完了: ${moved}件移動 / ${skipped}件スキップ" "Cyan"
    }
}

# ---- メイン ------------------------------------------------

Clear-Host
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        フォルダ整理スクリプト             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "  ★ プレビューモード（-DryRun）: ファイルは移動しません" -ForegroundColor Yellow
    Write-Host ""
}

# ログフォルダ作成
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Log "ログ保存先: $LogFile" "DarkGray"
}

# 対象フォルダを順番に整理
foreach ($folder in $TargetFolders) {
    Organize-Folder $folder
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "║  プレビュー完了。実行するには -DryRun     ║" -ForegroundColor Yellow
    Write-Host "║  オプションを外して再実行してください。   ║" -ForegroundColor Yellow
} else {
    Write-Host "║           すべての整理が完了しました！    ║" -ForegroundColor Green
    Write-Host "║   ログ: ドキュメント\FolderOrganizer\     ║" -ForegroundColor DarkGray
}
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
