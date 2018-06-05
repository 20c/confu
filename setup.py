
from setuptools import find_packages, setup


version = open('Facsimile/VERSION').read().strip()
requirements = open('Facsimile/requirements.txt').read().split("\n")
test_requirements = open('Facsimile/requirements-test.txt').read().split("\n")


setup(
    name='cfu',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='Configuration file validation and generation',
    long_description='',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages = find_packages(),
    include_package_data=True,
    url='https://github.com/20c/confu',
    download_url='https://github.com/20c/confu/%s' % version,

    install_requires=requirements,
    test_requires=test_requirements,

    zip_safe=True
)
