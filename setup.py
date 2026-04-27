''' 
This is the setup file for the project. This file is used to install the project as a package.
'''

from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path:str)-> List[str]:
    '''
    This funtion return the list of requirements in requirements.txt
    '''
    requirements = []
    try:
        with open(file_path, 'r') as file_obj:
            for line in file_obj: 
                req = line.strip()
                if not req or req.startswith('#'):
                    continue
                if req == "-e .":
                    continue
                requirements.append(req)  
        
    except FileNotFoundError:
        print(f"Error: requirements.txt not found at {file_path}")

    print(requirements) 
        


setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Palak Nagar",
    author_email="palaknaga13@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)

