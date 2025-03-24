# PowerShell script to set up SmartNav in the user's profile
$profilePath = $PROFILE  # Gets the user's profile path

# Define the SmartNav function
$smartNavFunction = @"
function smartnav {
    & python3 $PSScriptRoot\smartnav.py `$args
}
"@

# Write the function to the PowerShell profile
if (!(Test-Path $profilePath)) {
    New-Item -Path $profilePath -ItemType File -Force
}
Add-Content -Path $profilePath -Value $smartNavFunction

Write-Host "SmartNav has been added to your PowerShell profile. Restart PowerShell to use 'smartnav'."
