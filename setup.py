from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pypirccua",
    version="1.0.0",
    author="Ondrej Vanka",
    author_email="ondrej@vanka.net",
    description="A PyQt-based application for visualizing and analyzing relay counts from DB files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aknavj/pypirccua",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
        "matplotlib>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "pypirccua=pypirccua.__main__:main",
        ],
    },
    #package_data={
    #    "pypirccua": [
    #        "resources/*.png",
    #        "resources/*.ico",
    #    ],
    #},
)