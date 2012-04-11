// to run type: mongo houseprices update.js
// script to hack in the postcode part of the address as running a reg ex was taking too long

db.houses.find().forEach(function(data) {
    db.houses.update({_id:data._id},{$set:{postcode_part:data.address.split(" ")[data.address.split(" ").length - 1 ] } } );
});

