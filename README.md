# jsonld example generator

This Python script generates a JSON-LD template using an OSLO model. It starts with an OSLO RDF intermediary and a specified starting class (e.g., 'Verkeersmeting'). The script creates a template with blank node names, types, and properties, and links classes where necessary.

Objective: The output examples produced by this OSLO tool will be used to train a custom GPT model. This trained model can then convert unstructured data into OSLO-compliant Linked Data.


The purpose of this Python conversion tool is to generate jsonld templates based on an OSLO model. The process begins with the OSLO RDF intermediary (output from the OSLO toolchain) and a starting class. For example, if the starting class is "Verkeersmeting" in the OSLO model "Verkeersmetingen", the Python script will generate a complete OSLO jsonld template.

Starting with a class, it generates a blank node name (e.g. "@id": "_:Verkeersmeting001"), followed by its "@type" and all its properties. If a property or attribute points to another class, the blank node of that class is added as the value of that property.



The relationship between two classes is chosen in the direction starting from the starting class (e.g. Verkeersmeting). So the relation "UitgevoerdeObservatie" is not added to the element "Verkeersmeting". However, "UitgevoerdMet" is added as a relation between "Verkeersmeting" and "Sensor".

Currently, an inherited class is also added to the class (e.g. inherited_from": "Aanvullende properties kan je vinden in externe klasse : Observatie"). This allows for additional attributes from this inherited class to be added to this class. In the future, all attributes from a specific inherited class will be added.


```json

            "@id": "_:Verkeersmeting001",
            "@type": "Verkeersmeting",
            "inherited_from": "Aanvullende properties kan je vinden in externe klasse : Observatie",
            "Verkeersmeting.fenomeenTijd": "temporele entiteit",
            "Verkeersmeting.resultaat": "Any",
            "Verkeersmeting.resultaattijd": "Moment",
            "Verkeersmeting.resultaatkwaliteit": "Kwaliteitselement",
            "uitgevoerdDoor": "",
            "Verkeersmeting.metadata": "_:metadata001",
            "Verkeersmeting.geobserveerdKenmerk": "_:Verkeerskenmerk001",
            "Verkeersmeting.geobserveerdObject": "_:Verkeersobject001",
            "Verkeersmeting.gebruikteProcedure": "_:Observatieprocedure001",
            "Verkeersmeting.uitgevoerdMet": "_:Sensor001"

```


For commonly used data types, the Python script embeds the elaborated OSLO structure. For instance, when the datatype is “Punt”, the Python script adds this:

```json
            "Verkeersmeetpunt.geometrie": {
                "@type": "punt",
                "Geometrie.gml": {
                    "@value": "<gml:Point srsName=\"http:\\//www.opengis.net/def/crs/EPSG/0/4326\"><gml:coordinates>  Vul in: Lat Lon </gml:coordinates><gml:Point>",
                    "@type": "geosparql:gmlliteral"
                }
            },
```
Or for a “TaalString”:
```json
            "metadata.beschrijving": {
                "@language": "nl",
                "@value": "PAS AAN: vul beschrijving in"
            },
```
