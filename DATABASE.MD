## Database Schema

The database will contain 2 collections: Users and Recipes.

---

### Users collection:

##### Schema

```yaml
{
  "_id":          <ObjectID>,
  "name":         <string>,
  "email":        <string>,
  "password":     <string>,
  "address":      <string>  
}
```

##### Example

```yaml
{
  "_id":          <ObjectID>,
  "name":         "John Doe",
  "email":        "john@doe.com",
  "password":     "thisismypassword",
  "address":      "123 The Street, City, Country"  
}
```

---

### Recipes collection:

##### Schema

```yaml
{
  "_id":          <ObjectID>,
  "name":         <string>,
  "ingredients":  <string>,
  "instructions": <string>,
  "picture":      <ObjectID>
}
```

##### Example

```yaml
{
  "_id":          <ObjectID>,
  "name":         "Chocolate Cake",
  "ingredients":  "Milk, Flour Eggs,
  "instructions": <string>,
  "picture":      <ObjectID>

}
```