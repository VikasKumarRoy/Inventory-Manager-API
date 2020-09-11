### Getting started

* Clone the repo
* Setup your virtual environment

>required python version 3.6 and above
>```shell script
>pip install virtualenv
>virtualenv mypython
>```
>Activate: ``` source mypython/bin/activate ``` <br>
>Deactivate: ``` deactivate ``` [readmore](https://virtualenv.readthedocs.io/en/latest/virtualenv/)
 
* Install required libraries <br>
```pip install -r requirements.txt```

* Create a ```local.py``` file in ```hardwareManager/settings``` and paste ```local.py.template``` with your credentials in it.
* Apply migrations ```python manage.py migrate```
* Runserver ```python manage.py runserver```