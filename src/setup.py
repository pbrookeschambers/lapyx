from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'Embed Python code inside a LaTeX document'
LONG_DESCRIPTION = 'A preprocessor for LaTeX documents that allows for embedding Python code inside LaTeX documents.'

setup(
    name="lapyx",
    version=VERSION,
    author="Peter Brookes Chambers",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'latex', 'pdflatex']
)