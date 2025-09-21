from setuptools import setup, find_packages

setup(
    name="webhook-redirector",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.2",
        "requests>=2.31.0"
    ],
    entry_points={
        'console_scripts': [
            'webhook-redirector=app:main',
        ],
    },
    author="Webhook Redirector",
    description="A simple webhook that listens for incoming requests and redirects them to a specified URL",
    python_requires=">=3.6",
)