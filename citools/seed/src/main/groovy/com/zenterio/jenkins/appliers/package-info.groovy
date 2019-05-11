/**
<strong>Appliers</strong>
<p>
The purpose of the appliers is to provide a reusable way of building a model tree. Each applier should implement an
apply() method which takes data and a model. The applier then "applies" the data on the model, i.e. creates and
append appropriate models to the provided model.
<p>
Complex appliers can be allowed to have multiple apply methods, named
appropriately to indicate their purpose, as well as taking data in the
constructor if it helps readability.
<p>
With this pattern we can encapsulate logic for how to append a feature to a model. The encapsulation allow us to
easily change the behavior or introduce it in a new class without the need to create inheritance hierarchies,
only for this feature.

*/
package com.zenterio.jenkins.appliers;

