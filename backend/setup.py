from setuptools import setup, find_packages

setup(
    name='hki_signature_detection_api',
    version='1.0.0',
    description='Flask-based API for detecting signatures from PDF documents',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)