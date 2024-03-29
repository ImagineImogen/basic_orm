## A basic Object-Relational Mapper for sqlite

###### *A simple ORM  performing CRUD SQL requests.*

**How to use:**

```$ python basic_orm.py```

Please define your table schema inside the basic_orm.py file

Example entry: 

```
class User(Session):
    __tablename__ = "users"
    id = {'type': 'integer', "auto_add": True, "primary_key": True}
    name = {"type": "string", "length": 50}
    surname = {"type": "string", "length": 70}
    city = {"type" : "string", "length" : 50}
    city.update({'foreign_key' : 'city}) 
    #foreign key to another table column

```

Example API:
```
User.create_table()
User.delete_table()

User.add({'name': 'Vladimir', 'surname' :'Zelensky'})
User.update_all({'name': "Jonh", "surname": "Doe", 'age': '23',})
User.update_one({'name': 'Liza', 'surname': 'Janssen'}, {'id' : '2' })
User.select()
User.select('id', 'name')
User.select({"id": 5,"name": "Alicia"})
User.select("surname", {"id": 1,"name": "Romain"})
```
For more examples please check the example.py file

Be sure to close the connection when you no longer intend to use the ORM:
 
```
User.close()
```


## License
[MIT](https://choosealicense.com/licenses/mit/)