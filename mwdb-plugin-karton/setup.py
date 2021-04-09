from setuptools import setup

setup(name="mwdb-plugin-karton",
      version="1.1.0",
      description="Karton integration plugin for MWDB",
      author="CERT Polska",
      author_email="info@cert.pl",
      packages=["mwdb_plugin_karton"],
      include_package_data=True,
      install_requires=[
          "mwdb-core",
          "karton-core"
      ])
