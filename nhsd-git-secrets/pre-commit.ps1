# Pure PowerShell implementation of git-secrets pre-commit hook
# This script scans staged files for sensitive patterns defined in NHS rules

$ErrorActionPreference = "Stop"

function Get-StagedFiles {
    try {
        $stagedFiles = git diff --cached --name-only --diff-filter=ACM
        return $stagedFiles | Where-Object { $_ -and (Test-Path $_) }
    } catch {
        Write-Warning "Could not get staged files: $_"
        return @()
    }
}

function Get-SecretPatterns {
    $rulesFilePath = Join-Path $PSScriptRoot "nhsd-rules-deny.txt"
    
    if (-not (Test-Path $rulesFilePath)) {
        Write-Warning "Rules file not found at: $rulesFilePath"
        return @()
    }
    
    $patterns = Get-Content $rulesFilePath | Where-Object { 
        $_.Trim() -and -not $_.StartsWith('#') 
    }
    
    Write-Host "Loaded $($patterns.Count) secret detection patterns" -ForegroundColor Cyan
    return $patterns
}

function Get-AllowedPatterns {
    # Look for .gitallowed file in current directory or nhsd-git-secrets directory
    $allowedFiles = @(
        ".gitallowed",
        "nhsd-git-secrets/.gitallowed-base"
    )
    
    $allPatterns = @()
    
    foreach ($allowedFile in $allowedFiles) {
        if (Test-Path $allowedFile) {
            $patterns = Get-Content $allowedFile | Where-Object { 
                $_.Trim() -and -not $_.StartsWith('#') 
            }
            $allPatterns += $patterns
            Write-Host "Loaded $($patterns.Count) allowed patterns from $allowedFile" -ForegroundColor Cyan
        }
    }
    
    return $allPatterns
}

function Test-FileAllowed {
    param(
        [string]$FilePath,
        [string[]]$AllowedPatterns
    )
    
    foreach ($pattern in $AllowedPatterns) {
        # Handle patterns with colon separator (file:line format)
        if ($pattern -match '^(.+?):(.*)$') {
            $filePattern = $matches[1]
            $linePattern = $matches[2]
            
            # Convert wildcard patterns to regex
            $fileRegex = $filePattern -replace '\*', '.*' -replace '\.', '\.'
            
            # Check if file matches the allowed file pattern
            if ($FilePath -match $fileRegex) {
                return $true, $filePattern, $linePattern
            }
        }
        # Handle patterns without colon (file-only patterns)
        else {
            # Convert wildcard patterns to regex
            $fileRegex = $pattern -replace '\*', '.*' -replace '\.', '\.'
            
            # Check if file matches the pattern
            if ($FilePath -match $fileRegex) {
                return $true, $pattern, '*'
            }
        }
    }
    
    return $false, $null, $null
}

function Test-LineAllowed {
    param(
        [string]$Line,
        [string]$LinePattern
    )
    
    # If line pattern is *, allow all lines in the file
    if ($LinePattern -eq '*') {
        return $true
    }
    
    # If line pattern is empty, allow all lines
    if (-not $LinePattern) {
        return $true
    }
    
    # Check if the line matches the allowed pattern
    return $Line -match $LinePattern
}

function Test-FileForSecrets {
    param(
        [string]$FilePath,
        [string[]]$Patterns,
        [string[]]$AllowedPatterns
    )
    
    $violations = @()
    
    # Check if the entire file is allowed
    $fileAllowed, $filePattern, $linePattern = Test-FileAllowed -FilePath $FilePath -AllowedPatterns $AllowedPatterns
    if ($fileAllowed -and $linePattern -eq '*') {
        Write-Host "     Skipping (allowed): $FilePath" -ForegroundColor DarkGray
        return @()
    }
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return @() }
        
        $lineNumber = 1
        foreach ($line in ($content -split "`n")) {
            foreach ($pattern in $Patterns) {
                if ($line -match $pattern) {
                    # Check if this specific line/match is allowed
                    $lineAllowed = $false
                    if ($fileAllowed) {
                        $lineAllowed = Test-LineAllowed -Line $line -LinePattern $linePattern
                    }
                    
                    if (-not $lineAllowed) {
                        $violations += [PSCustomObject]@{
                            File = $FilePath
                            Line = $lineNumber
                            Pattern = $pattern
                            Match = $matches[0]
                            Content = $line.Trim()
                        }
                    }
                }
            }
            $lineNumber++
        }
    } catch {
        Write-Warning "Could not scan file $FilePath : $_"
    }
    
    return $violations
}

function Write-ViolationReport {
    param([array]$Violations)
    
    Write-Host ""
    Write-Host "SECRETS DETECTED!" -ForegroundColor Red -BackgroundColor Yellow
    Write-Host ""
    
    $groupedViolations = $Violations | Group-Object File
    
    foreach ($fileGroup in $groupedViolations) {
        Write-Host "File: $($fileGroup.Name)" -ForegroundColor Red
        Write-Host "   $('-' * 50)" -ForegroundColor DarkRed
        
        foreach ($violation in $fileGroup.Group) {
            Write-Host "   Line $($violation.Line): " -ForegroundColor Yellow -NoNewline
            Write-Host "$($violation.Match)" -ForegroundColor Red
            Write-Host "   Pattern: $($violation.Pattern)" -ForegroundColor DarkGray
            Write-Host ""
        }
    }
    
    Write-Host "Found $($Violations.Count) potential secret(s) in $($groupedViolations.Count) file(s)" -ForegroundColor Red
    Write-Host "Please remove these secrets before committing!" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
try {
    Write-Host "NHS Git-Secrets: Scanning staged files for sensitive data..." -ForegroundColor Cyan
    
    $stagedFiles = Get-StagedFiles
    if ($stagedFiles.Count -eq 0) {
        Write-Host "No staged files to scan" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Scanning $($stagedFiles.Count) staged file(s)..." -ForegroundColor Cyan
    
    $patterns = Get-SecretPatterns
    if ($patterns.Count -eq 0) {
        Write-Warning "No patterns loaded, skipping scan"
        exit 0
    }
    
    # Load allowed patterns
    $allowedPatterns = Get-AllowedPatterns
    if ($allowedPatterns.Count -gt 0) {
        Write-Host "Using .gitallowed exclusions" -ForegroundColor Cyan
    }
    
    $allViolations = @()
    foreach ($file in $stagedFiles) {
        Write-Host "   Checking: $file" -ForegroundColor DarkCyan
        $violations = Test-FileForSecrets -FilePath $file -Patterns $patterns -AllowedPatterns $allowedPatterns
        $allViolations += $violations
    }
    
    if ($allViolations.Count -eq 0) {
        Write-Host ""
        Write-Host "No secrets detected in staged files!" -ForegroundColor Green
        Write-Host ""
        exit 0
    } else {
        Write-ViolationReport -Violations $allViolations
        exit 1
    }
    
} catch {
    Write-Error "An error occurred during secret scanning: $_"
    exit 1
}
