from setuptools import setup, find_packages                                                                                         
                                                                                                                     
setup(                                                                                                               
    name = 'Statistical Contextual Structure of Representation',                                                                                                   
    packages = ['scsr_api'],
    scripts=['manage.py'],                                                                                             
    version = "0.0.1",                                                                                               
    license = "MIT",                                                                                             
    author = "Rodrigo Domingues (Lord Spy)",                                                                                             
    author_email = "lordspy@gmail.com",                                                                              
    description = "RESTful API system to provide classification and quantification services for game studies" ,
    keywords = "GameStudies SCSR Classification Quantification Categorization",                                                                                                                
    py_modules = ['scsr_api']                                                                                            
)                                              