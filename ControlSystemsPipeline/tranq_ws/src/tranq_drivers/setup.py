from setuptools import setup
package_name = 'tranq_drivers'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@example.com',
    description='Real hardware drivers for the TranquilShot drone system',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'camera_driver     = tranq_drivers.camera_driver:main',
            'vl53l1x_driver    = tranq_drivers.vl53l1x_driver:main',
            'optical_flow_node = tranq_drivers.optical_flow_node:main',
        ],
    },
)
