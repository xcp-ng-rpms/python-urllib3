import sys
import subprocess


def build_wheel(*, wheeldir, stdout=None):
    command = (
        sys.executable,
        '-m', 'pip',
        'wheel',
        '--wheel-dir', wheeldir,
        '--no-deps',
        '--disable-pip-version-check',
        '--no-clean',
        '--verbose',
        '.',
    )
    cp = subprocess.run(command, stdout=stdout)
    return cp.returncode


if __name__ == '__main__':
    sys.exit(build_wheel(wheeldir=sys.argv[1]))

