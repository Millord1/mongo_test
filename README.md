```bash
mongoimport \
  --db new_york \
  --collection restaurants \
  --file Restaurants.json \
  --jsonArray
```

```bash
db.movies.distinct("title").length
```
résultat: 3883

## Question 14

```javascript
db.users.updateMany(
  {},
  [
    {
      $set: {
        num_ratings: { $size: "$movies" }
      }
    }
  ]
)
```

```javascript
db.users.countDocuments({
  num_ratings: { $gte: 90 }
})
```
3133

## Question 16

```javascript
movie_lens> db.users.aggregate([
|   { $unwind: "$movies" },
|   { $match: { "movies.movieid": 296 } },
|   {
|     $group: {
|       _id: "$movies.movieid",
|       average_rating: { $avg: "$movies.rating" }
|     }
|   }
| ])
[ { _id: 296, average_rating: 4.278212805158913 } ]

```

## Question 17

```javascript
db.users.aggregate([
  {
    $project: {
      _id: 0,
      id: "$_id",
      name: 1,
      max_rating: { $max: "$movies.rating" },
      min_rating: { $min: "$movies.rating" },
      avg_rating: { $avg: "$movies.rating" }
    }
  },
  {
    $sort: { avg_rating: 1 }
  }
])
```

```bash
 {
    name: 'Tomoko Barrett',
    id: 5944,
    max_rating: 5,
    min_rating: 1,
    avg_rating: 2.2
  },

```