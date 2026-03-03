from setuptools import setup, find_packages, Extension

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

ext_modules = []
try:
    from Cython.Build import cythonize

    ext_modules = cythonize(
        [Extension("mkdocs_dbml_plugin._routing", ["mkdocs_dbml_plugin/_routing.pyx"])],
        compiler_directives={"language_level": "3"},
    )
except ImportError:
    pass

setup(
    name="mkdocs-dbml-plugin",
    version="1.0.0",
    author="ZhuchkaTriplesix",
    author_email="mrlololoshka94@gmail.com",
    description="MkDocs plugin to render DBML as interactive ERD diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZhuchkaTriplesix/mkdocs-dbml",
    packages=find_packages(),
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mkdocs>=1.0.0",
        "numpy>=1.20.0",
        "pydbml>=1.0.0",
    ],
    entry_points={
        "mkdocs.plugins": [
            "dbml = mkdocs_dbml_plugin.plugin:DbmlPlugin",
        ]
    },
    include_package_data=True,
)
