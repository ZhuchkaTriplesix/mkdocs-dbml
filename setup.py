from setuptools import setup, find_packages, Extension

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
    packages=find_packages(),
    ext_modules=ext_modules,
    include_package_data=True,
)
