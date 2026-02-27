from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-dbml-plugin",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MkDocs plugin to render DBML (Database Markup Language) as beautiful HTML tables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mkdocs-dbml-plugin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mkdocs>=1.0.0",
        "pydbml>=1.0.0",
    ],
    entry_points={
        "mkdocs.plugins": [
            "dbml = mkdocs_dbml_plugin.plugin:DbmlPlugin",
        ]
    },
    include_package_data=True,
)
