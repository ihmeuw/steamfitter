from pathlib import Path

from setuptools import find_packages, setup

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"

    about = {}
    with (src_dir / "steamfitter" / "__about__.py").open() as f:
        exec(f.read(), about)

    with (base_dir / "README.rst").open() as f:
        long_description = f.read()

    install_requirements = [
        "click",
        "loguru",
        "numpy",
        "pandas",
        "pathos",
        "pyyaml>=5.1",
        "tqdm",
    ]

    test_requirements = [
        "pytest",
        "pytest-mock",
    ]

    doc_requirements = [
        "sphinx>=4.0",
        "sphinx-rtd-theme",
        "sphinx-click",
    ]

    internal_requirements = [
        "jobmon[ihme]==3.0.5",
        "db_queries>=25.2.0,<26",
    ]

    other_dev_requirements = [
        "black",
        "isort",
    ]

    setup(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__summary__"],
        long_description=long_description,
        license=about["__license__"],
        url=about["__uri__"],
        author=about["__author__"],
        author_email=about["__email__"],
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        include_package_data=True,
        install_requires=install_requirements,
        tests_require=test_requirements,
        extras_require={
            "docs": doc_requirements,
            "test": test_requirements,
            "internal": internal_requirements,
            "dev": (doc_requirements + test_requirements + other_dev_requirements),
        },
        zip_safe=False,
    )
