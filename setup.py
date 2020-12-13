import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt", "r") as file:
    required_packages = file.read().splitlines()

setuptools.setup(
    name="labscribe",
    version="0.3.3",
    author="Jay Morgan",
    author_email="jay.p.morgan@outlook.com",
    description="A small package for managing python experiment scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaypmorgan/labscribe",
    packages=setuptools.find_packages(),
    python_requires=">=3",
    install_requires=required_packages,
    include_package_data=True,
    package_data={"labscribe": ["labscribe/data/*.sql"]},
)
