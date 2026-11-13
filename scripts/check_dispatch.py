"""Optional test against an explicitly selected Dispatch checkout; no cloud calls."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from new_project import generate

ROOT = Path(__file__).resolve().parents[1]


def check(dispatch_root):
    dispatch_root = dispatch_root.resolve()
    if not (dispatch_root / 'internal/solution/manifest.go').is_file():
        raise ValueError('--dispatch-root must select a box-dispatch source checkout')
    with tempfile.TemporaryDirectory(prefix='agentic-dispatch-check-') as temp:
        temp = Path(temp)
        project = generate('dispatch-smoke', 'Dispatch Smoke', 'Salesforce', temp / 'project')
        subprocess.run(['git', 'init', '-b', 'main', str(project)], check=True, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=project, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Template Compatibility Test', '-c', 'user.email=template-test@example.invalid',
                        'commit', '-m', 'Temporary compatibility fixture'], cwd=project, check=True, capture_output=True)
        probe = temp / 'probe'; probe.mkdir()
        shutil.copyfile(ROOT / 'tools/dispatch-compat/main.go', probe / 'main.go')
        module = ('module github.com/unofficialbox/box-dispatch/template-compat\n\ngo 1.26\n\n'
                  'require github.com/unofficialbox/box-dispatch v0.0.0\n\n'
                  'replace github.com/unofficialbox/box-dispatch => ' + json.dumps(str(dispatch_root)) + '\n')
        (probe / 'go.mod').write_text(module)
        environment = {**os.environ, 'GOWORK': 'off', 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'Never'}
        subprocess.run(['go', 'run', '-mod=mod', '.', str(project), str(temp / 'dispatch-package')],
                       cwd=probe, env=environment, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dispatch-root', required=True, type=Path)
    args = parser.parse_args()
    check(args.dispatch_root)
