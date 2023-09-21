#!/usr/bin/env python
import sys
from pathlib import Path
from ksconf.builder import BuildManager, VERBOSE, QUIET, default_cli
from ksconf.builder.steps import clean_build, copy_files, pip_install

manager = BuildManager()

APP_FOLDER = "jmespath"
SPL_NAME = "jmespath-for-splunk-{{version}}.tgz"
SOURCE_DIR = "."

REQUIREMENTS = "requirements.txt"

# Files needed to support the build process (but not in the final package)
BUILD_FILES = [
    REQUIREMENTS,
]

COPY_FILES = [
    "*.md",
    "appserver/",
    "bin.d/",
    "default.d/",
    "lookups/*.csv",
    "metadata.d/",
    "README/",
    "static/",
] + BUILD_FILES


@manager.cache([REQUIREMENTS], ["lib/"], timeout=7200)
def python_packages(step):
    # Sticking with the defaults
    pip_install(step, REQUIREMENTS, "lib",
                handle_dist_info="remove"  # vs 'rename'
                )


def package_spl(step):
    top_dir = step.dist_path.parent
    release_path = top_dir / ".release_path"
    release_name = top_dir / ".release_name"
    step.run(sys.executable, "-m", "ksconf", "package",
             "--file", step.dist_path / SPL_NAME,   # Path to created tarball
             "--app-name", APP_FOLDER,              # Top-level directory name
             "--block-local",                       # Build from version control should have no 'local' folder
             "--layer-method", "dir.d",
             "--blocklist", REQUIREMENTS,           # No need to distribute this
             "--release-file", str(release_path),
             ".")
    # Provide the dist file as a short name too (useful for some CI/CD tools)
    path = release_path.read_text()
    short_name = Path(path).name
    release_name.write_text(short_name)


def build(step, args):
    """ Build process """
    # Step 1:  Clean/create build folder
    clean_build(step)

    # Step 2:  Copy files from source to build folder
    copy_files(step, COPY_FILES)

    # Step 3:  Install Python package dependencies
    python_packages(step)

    # Step 4: Build tarball
    package_spl(step)


if __name__ == '__main__':
    # Tell build manager where stuff lives
    manager.set_folders(SOURCE_DIR, "build", "dist")

    # Launch build CLI
    default_cli(manager, build)
