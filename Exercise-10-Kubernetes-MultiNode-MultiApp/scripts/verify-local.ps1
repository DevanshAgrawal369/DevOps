$ErrorActionPreference = 'Continue'

$exerciseRoot = Split-Path -Parent $PSScriptRoot
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonLauncher) {
    throw 'Python launcher `py` was not found. Install Python 3 and rerun this script.'
}

 $tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
 $venvPath = Join-Path $tempBase ("exercise10-validation-" + [Guid]::NewGuid().ToString('N'))
 try {
    Write-Host "== Create isolated validation environment =="
    & py -3 -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create a temporary Python virtual environment.'
    }
    $python = Join-Path $venvPath 'Scripts\python.exe'
    foreach ($requirements in @(
        'app-a-product-catalog\requirements.txt',
        'app-b-shopping-cart\requirements.txt',
        'requirements-dev.txt'
    )) {
        & $python -m pip install --disable-pip-version-check -r (Join-Path $exerciseRoot $requirements)
        if ($LASTEXITCODE -ne 0) {
            throw "Pinned dependency installation failed: $requirements"
        }
    }

    foreach ($application in @('app-a-product-catalog', 'app-b-shopping-cart')) {
        $applicationPath = Join-Path $exerciseRoot $application
        Write-Host "== Unit tests: $application =="
        Push-Location $applicationPath
        try {
            # Direct unittest progress to stdout for clean PowerShell output.
            $runner = "import sys,unittest; suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite); sys.exit(not result.wasSuccessful())"
            & $python -c $runner
            if ($LASTEXITCODE -ne 0) {
                throw "Unit tests failed for $application."
            }
        }
        finally {
            Pop-Location
        }
    }

    Write-Host '== Kubernetes YAML syntax and requirement checks =='
    $yamlCheck = @'
from pathlib import Path
import sys
import yaml

root = Path(sys.argv[1])
files = sorted((root / "k8s").glob("*.yaml"))
documents = []
for path in files:
    parsed = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    documents.extend(doc for doc in parsed if doc is not None)
    print(f"YAML OK: {path.relative_to(root)} ({len(parsed)} document(s))")

assert len(documents) == 5, f"Expected 5 Kubernetes objects; found {len(documents)}"
expected = {"product-catalog": 2, "shopping-cart": 3}
for name, replicas in expected.items():
    deployment = next(
        doc for doc in documents
        if doc.get("kind") == "Deployment" and doc["metadata"]["name"] == name
    )
    assert deployment["spec"]["replicas"] == replicas
    pod_spec = deployment["spec"]["template"]["spec"]
    terms = pod_spec["affinity"]["podAntiAffinity"][
        "requiredDuringSchedulingIgnoredDuringExecution"
    ]
    assert terms[0]["topologyKey"] == "kubernetes.io/hostname"
    assert terms[0]["labelSelector"]["matchLabels"]["app.kubernetes.io/name"] == name
print("Manifest checks OK: replica counts, required hostname anti-affinity, and selectors.")
'@
    $yamlCheck | & $python - $exerciseRoot
    if ($LASTEXITCODE -ne 0) {
        throw 'YAML parsing or manifest requirement checks failed.'
    }

    Write-Host 'Local unit tests and manifest checks passed in a temporary virtual environment. This script does not contact or modify a Kubernetes cluster.'
 }
 finally {
    if (Test-Path -LiteralPath $venvPath) {
        $resolvedVenv = (Resolve-Path -LiteralPath $venvPath).Path
        if (-not $resolvedVenv.StartsWith($tempBase, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw 'Refusing to remove a path outside the system temporary directory.'
        }
        Remove-Item -LiteralPath $resolvedVenv -Recurse -Force
    }
}
