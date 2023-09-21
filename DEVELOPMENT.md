# Developing jmespath


## Python packages

Externally required Python packages are listed in the [requirements.txt](./requirements.txt) file.
These packages are automatically downloaded and installed into the `lib` folder of the addon during the build process.

**Gotchas:**  Avoid packages that *only* work on a specific version of Python or has OS-specific compiled libraries.
Python 2.7 support is going away for more and more packages, so pinning older versions may be required until targeting only Splunk 8+ for compatibility.
The default build script only builds with a single version of Python, and doesn't attempt to separate packages based on OS or Python version.

## Development

Setup a local virtual environment in the top level of the package to install the necessary build and runtime requirements.

    python3 -m venv venv
    . venv/bin/activate
    python -m pip install -U -r requirements-dev.txt

Setup pre-commit

    pre-commit install --install-hooks


## Building

You can build JMESPath for Splunk using the following steps:

    ./build.py && "$SPLUNK_HOME/bin/splunk" install app "$(<.release_path)" -update 1

The above command will build and (re)install the app into a running Splunk development instance.

## Releasing

The app version number can be updated using the `bumpversion` and pushed upstream using `git`.  Here's a common example:

    bumpversion patch    # <-- Pick major, minor, patch
    git push origin main --tags

## Tools

 * [Cookiecutter](https://github.com/audreyr/cookiecutter) is use to kickstart the development of new addons.
 * [bump2version](https://pypi.org/project/bump2version/) Version bump your addon with a single command!
 * [ksconf](https://ksconf.readthedocs.io/) Kintyre Splunk CONF tool
 * [pre-commit](https://pre-commit.com/) a framework for managing and maintaining pre-commit hooks for git.
