# 

## Setup 

1. Install asdf & python plugin
2. Install python
   * `asdf install`
3. Install poetry
4. Activate virtual-env
   * `poetry env use "$(cat ./.tool-versions | grep "python" | cut -d " " -f 2)"`
5. Install python packages
   * `poetry install`
