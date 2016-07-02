from distutils.core import setup, Extension

where_ext = Extension(
    "where_", ["where_.c", "where.c"], extra_link_args=["-lX11"])

setup(
    ext_modules=[where_ext],
)
