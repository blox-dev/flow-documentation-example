# Part 1: Maintainer

## Setup

Step 0. [Download the `flow-documentation` extension.](../README.md)

Step 1. Download a copy of the `Odoo` repository to your machine. The latest version of `Odoo` is available [here](`https://github.com/odoo/odoo`).

(We tested this extension on the most recent functional version of Odoo as of [April 24, 2020](https://github.com/odoo/odoo/tree/436be43d49260c905d37927b21b75404f4ccfc1f))

Note: The functionality of the `Odoo` app on your machine is **NOT** a prerequisite for the extension to operate as intended. However, if you wish to enable `Odoo` on your machine, you can refer to the [Setup Guide](https://www.odoo.com/documentation/17.0/developer/tutorials/setup_guide.html).

Step 2. Add `maintainerMap.json` to the parent folder of the `Odoo` repository.

Step 3. Open the parent folder with `VSCode`. The `Maintainer` extension should prompt you to choose a file as your maintainer map. Navigate and choose `maintainerMap.json` as the file.

Note: If the prompt does not popup by itself, you can trigger it manually by opening the editor command selector within VSCode `(Ctrl + Shift + P)` and select `Choose Maintainer File`.

Step 4. Open the `Maintainer` sidebar and start exploring!

## Features:
- The `Maintainer` sidebar shows by default the most active maintainers (based on the number of assigned files / folders).
- Right-clicking on a file or folder reveals the `Find maintainer` button

## Future ideas:
- In case a file does not have a maintainer, choose as fallback the most active recent maintainer who has edited that file (with git).
