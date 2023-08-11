Multitasking SSIM
=================

This project has been crafted to harness the power of the Python asyncio library, enabling the concurrent processing of images downloaded from the internet. It's required the utilization of Python 3.11.

Underneath the surface, the program excels at parallel image downloading based on the configuration settings. Following this, it performs intricate image comparison using metrics like MSE, SSIM, and PSNR against a reference image. The resulting data is exported to a CSV file.


Installation
------------

1.  Clone this repository

2.  Navigate to the project directory:

    `cd multitasking-ssim`

3.  Install the project dependencies using Poetry:

    `poetry install`

Usage
----

You can use the Multitasking SSIM CLI. To start the CLI, run:

    poetry run cli

Read the .config.example.yml file for a better knowledge about what must be set.

Available Commands
------------------

* `ai compare_images`: Compare the images and export the results to a CSV.

Flags and Options
----------------

* `-c`, `--config`: The configuration file path (YAML)
