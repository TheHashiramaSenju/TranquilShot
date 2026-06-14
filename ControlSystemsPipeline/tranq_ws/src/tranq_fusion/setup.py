from setuptools import setup, find_packages
import os
package_name = 'tranq_fusion'
setup(
    name=package_name, version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), ['config/fusion_params.yaml']),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='you', maintainer_email='you@example.com',
    description='Sensor fusion gates for TranquilShot',
    license='Apache-2.0',
    entry_points={'console_scripts': ['fusion_node = tranq_fusion.fusion_node:main']},
)
