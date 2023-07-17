from setuptools import setup

setup(
    name="easylabwork",
    version="0.7.0",
    author="Jeremy Fix",
    author_email="jeremy.fix@centralesupelec.fr",
    packages=["easylabwork"],
    license="LICENSE",
    description="Python package from making it easy to generate lab work codes",
    entry_points={"console_scripts": ["easylabwork=easylabwork.easylabwork:main"]},
)
