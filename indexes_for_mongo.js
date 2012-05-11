//db.houses.findOne()
//db.getCollectionNames().forEach(function(collection) {
//  print(collection);
//});

// Add index:
db.houses.ensureIndex({'postcode':1, 'dateadded':1})

db.houses.ensureIndex({'postcode_part':1, 'dateadded':1})

