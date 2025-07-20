from setuptools import setup, find_packages

setup(
    name="pmgmt-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "python-multipart",
        "sqlalchemy",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
    ],
    entry_points={
        "console_scripts": [
            "pmgmt-service=pmgmt_service.main:main",
        ],
    },
    author="Your Organization",
    author_email="your.email@example.com",
    description="Patch Management Service for collecting and displaying package update information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/pmgmt-service",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)