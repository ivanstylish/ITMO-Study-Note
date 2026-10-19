param(
    [ValidateSet('run', 'shell', 'check', 'test', 'verify', 'regression', 'demo')]
    [string]$Action = 'run',
    [ValidateSet('intro', 'shebang')]
    [string]$Project = 'intro'
)

$ErrorActionPreference = 'Stop'
$xv6Source = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\xv6-$Project"))
if (-not (Test-Path -LiteralPath (Join-Path $xv6Source 'Makefile'))) {
    throw "xv6 source directory was not found: $xv6Source"
}
if ($Action -eq 'verify' -and $Project -ne 'intro') {
    throw 'The one-byte pipe check belongs to the intro project.'
}
if ($Action -eq 'demo' -and $Project -ne 'shebang') {
    throw 'The shebang demonstration belongs to the shebang project.'
}

$xv6DockerArgs = @('run', '--rm', '--platform', 'linux/amd64')
if ($Action -in @('run', 'shell')) {
    $xv6DockerArgs += '-it'
}
$xv6DockerArgs += @(
    '--mount', "type=bind,source=$xv6Source,target=/xv6",
    '--mount', "type=bind,source=$PSScriptRoot,target=/lab-notes",
    '--workdir', '/xv6',
    'vityamand/xv6@sha256:1bc77fa40a642500bd4dbba1412e1575303976b0dec48f047eaf8237fd93dd69'
)

switch ($Action) {
    'run' { $xv6DockerArgs += @('make', 'qemu', 'CPUS=3') }
    'shell' { $xv6DockerArgs += '/bin/bash' }
    'check' { $xv6DockerArgs += @('sh', '/lab-notes/scripts/check-env.sh') }
    'test' {
        $xv6DockerArgs += @('python3', '/lab-notes/scripts/check-lab.py', $Project, 'functional')
    }
    'verify' {
        $xv6DockerArgs += @('python3', '/lab-notes/scripts/verify-pingpong.py')
    }
    'regression' {
        $xv6DockerArgs += @('python3', '/lab-notes/scripts/check-lab.py', $Project, 'regression')
    }
    'demo' {
        $xv6DockerArgs += @(
            'python3', '/lab-notes/scripts/check-qemu.py', 'demo',
            '--log', '/lab-notes/logs/shebang-demo-qemu.log'
        )
    }
}

& docker @xv6DockerArgs
if ($LASTEXITCODE -ne 0) {
    throw "The xv6 container exited with code $LASTEXITCODE"
}
