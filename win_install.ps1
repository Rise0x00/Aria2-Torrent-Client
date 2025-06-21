function Write-Status([string]$message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-ErrorStatus([string]$message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

Write-Status "Checking Scoop installation..."

if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Status "Scoop already installed."
} else {
    Write-Status "Scoop not installed. Installing..."


    try {
        Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
        irm get.scoop.sh | iex
        Write-Status "Scoop succesfully installed."
    } catch {
        Write-ErrorStatus "Error Scoop installation: $_"
        exit 1
    }
}

Write-Status "Checking aria2 installation..."

if (scoop list aria2 -ErrorAction SilentlyContinue) {
    Write-Status "aria2 already installed."
} else {
    Write-Status "aria2 not installed. Installing via Scoop..."

    try {
        scoop install aria2
        Write-Status "aria2 succesfully installed."
    } catch {
        Write-ErrorStatus "Error aria2 installation: $_"
        exit 1
    }
}

Write-Status "Installing has been completed successfully!"