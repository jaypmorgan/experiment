import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="labscribe",
    version="0.0.1",
    author="Jay Morgan",
    author_email="jay.p.morgan@outlook.com",
    description="A small package for managing python experiment scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaypmorgan/labscribe",
    packages=setuptools.find_packages(),
    python_requires=">=3",
)
