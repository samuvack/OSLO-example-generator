import subprocess
import json

def extract_data(json_file, output_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        with open(output_file, 'w') as file:
            for item in data:
                if item.get("type") == "ap":
                    name = item.get("name", "No Name")
                    eap = item.get("eap", "No Name")
                    diagram = item.get("diagram", "No Diagram")
                    file.write(f"Name: {name}, Diagram: {diagram}\n")
                    return name, eap, diagram

    except FileNotFoundError:
        print(f"File {json_file} not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")


def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def main():
    json_file = 'Verkeersmetingen.json'
    output_file = 'extracted_data.txt'
    name, eap, diagram = extract_data(json_file, output_file)
    
    # Convert to json-ld app
    run_command("node ../../packages/oslo-converter-uml-ea/bin/runner.js --umlFile " + eap + " --diagramName " + diagram + " --outputFile " + name + ".jsonld --specificationType ApplicationProfile --outputFormat application/ld+json --publicationEnvironment 'https://data.vlaanderen.be#' --versionId '" + name + "'")

    # Convert to json-ld voc
    #run_command("node ../../packages/oslo-converter-uml-ea/bin/runner.js --umlFile OSLO-Weg.eap --diagramName wegenregister_applicatieprofiel --outputFile output_voc.jsonld --specificationType Vocabulary --outputFormat application/ld+json --publicationEnvironment 'https://implementatie.data.vlaanderen.be#' --versionId 'wegenregister'")

    # Convert to RESPEC html impl
    #run_command("node ../../packages/oslo-generator-respec-html/bin/runner.js --input wegenregister_output.jsonld --output wegenregister_output.html --specificationType ApplicationProfile --language nl --specificationName 'Applicatieprofiel wegenregister'")

    # Convert to RESPEC html voc
    #run_command("node ../../packages/oslo-generator-respec-html/bin/runner.js --input output_voc.jsonld --output output_voc.html --specificationType Vocabulary --language nl --specificationName 'Vocabularium wegenregister'")



    start_class = "Verkeersmeting"

    # Function to read the JSON-LD file
    def read_jsonld_file(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data


    def create_jsonld_with_context(jsonld_data, context):
        jsonld_with_context = {
            "@context": [context],
            "@graph": jsonld_data
        }
        return jsonld_with_context

    def find_value_for_key(dictionary, key_to_find):
        return dictionary.get(key_to_find)

    # Function to extract classes with their names and properties
    def extract_classes_and_properties_from_jsonld(data):
        classes = {}
        classes_data = data.get('classes', [])

        
        attributes_data = data.get('attributes', [])

        # Extract classes with names
        for class_item in classes_data:
            class_id = class_item.get('@id')
            class_name = next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), '')
            if class_name:
                classes[class_name] = {
                    'id': class_id,
                    'properties': [],
        }

        # Extract properties and associate them with classes using class names
        for attribute in attributes_data:
            domain_id = attribute.get('domain', {}).get('@id')
            property_name = next((label['@value'] for label in attribute.get('vocLabel', []) if label.get('@language') == 'nl'), '')
            class_name = next((name for name, details in classes.items() if details['id'] == domain_id), None)
            if class_name and property_name:
                classes[class_name]['properties'].append(property_name)


        return classes, attributes_data

    # Function to write the extracted data to a JSON-LD file
    def write_to_jsonld_file(data, output_file_path):
        with open(output_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def reorder_dictionary_based_on_values(original_dict, specified_value):
        # Eerst alle elementen selecteren waarvan value[0] gelijk is aan de opgegeven waarde
        selected_elements = {k: v for k, v in original_dict.items() if v[0] == specified_value}

        # Selecteer vervolgens elementen waarvan value[0] gelijk is aan value[1] van eerder geselecteerde elementen
        for key, value in original_dict.items():
            if value[0] in [val[1] for val in selected_elements.values()]:
                selected_elements[key] = value

        return selected_elements

    def filter_properties_by_range(attributes_data, datatypes_dict):
        property_name_to_range_id = {}
        for property_name, range_id in attributes_data.items():
            # Voeg het element alleen toe als range_id niet in datatypes_dict voorkomt
            if range_id not in datatypes_dict:
                property_name_to_range_id[property_name] = range_id

        return property_name_to_range_id


    def create_datatypes_dict(datatypes):
        datatypes_dict = {}
        for item in datatypes:
            key = item.get("@id")

            # Controleer of 'vocLabel' aanwezig is, zo niet, gebruik 'diagramLabel'
            if 'vocLabel' in item and item['vocLabel']:
                voc_label = next((label["@value"] for label in item["vocLabel"] if label["@language"] == "nl"), None)
                if voc_label:
                    datatypes_dict[key] = voc_label
            elif 'diagramLabel' in item and item['diagramLabel']:
                # Neem aan dat 'diagramLabel' een lijst is en neem het '@id' van het eerste element
                diagram_label_id = item['diagramLabel'][0].get('@value') if isinstance(item['diagramLabel'], list) else item['diagramLabel'].get('@value')
                if diagram_label_id:
                    datatypes_dict[key] = diagram_label_id

        return datatypes_dict


    def unique_dict(d):
        seen = set()
        remove_d = {}
        unique_d = {}

        for key, value in d.items():
            # Vervang None door een unieke placeholder om sortering en vergelijking mogelijk te maken
            value_with_placeholder = tuple(sorted((v if v is not None else 'NonePlaceholder' for v in value)))
            if value_with_placeholder not in seen:
                seen.add(value_with_placeholder)
                unique_d[key] = value
            else:
                remove_d[key] = value
                

        return unique_d, remove_d

    def to_camel_case(input_string):
        # Verwijder het "^"-teken
        camel_case_string = input_string.replace("^", "")
        if " " in input_string:
            # Splits de string op spaties en zet het eerste teken van elk woord in hoofdletters
            words = camel_case_string.split()
            camel_case_string = words[0].lower() + ''.join(word.capitalize() for word in words[1:])

        return camel_case_string

    # Functie om de gewenste informatie uit elk woordenboek te extraheren
    def extract_range_domain_from_attributes(data):
        new_dict = {}
        for item in data:
            voc_label = item.get('vocLabel', [{}])[0].get('@value', None)
            domain_id = item.get('domain', {}).get('@id', None)
            range_id = item.get('range', {}).get('@id', None)
            if voc_label and domain_id and range_id:
                new_dict[voc_label] = [domain_id, range_id]
        return new_dict

    def get_first_elements(list_of_lists):
        return [sublist[0] for sublist in list_of_lists]

    def get_second_elements(list_of_lists):
        return [sublist[1] for sublist in list_of_lists]


    def loop_datatypes(datatypes_dict, result_dict, datatypes_yellow, types_dict,range_id, class_name):
        for i in datatypes_yellow.get(types_dict[range_id]):
            if datatypes_dict.get(i[2]) == "TaalString":
                result_dict[f'{i[0]}'] = {"@language": "nl", "@value": "PAS AAN: vul in"}
            elif datatypes_dict.get(i[2]) == "String":
                result_dict[f'{i[0]}'] = "PAS AAN: vul in"
            elif datatypes_dict.get(i[2]) == "URI":
                result_dict[f'{i[0]}'] = "PAS AAN: vul URI in"
            elif datatypes_dict.get(i[2]) == "punt":
                result_dict[f'{i[0]}'] = {"@type": "punt",
                                          "Geometrie.gml": {
                                            "@value": "<gml:Point srsName=\"http:\\//www.opengis.net/def/crs/EPSG/0/4326\"><gml:coordinates>  Vul in: Lat Lon </gml:coordinates><gml:Point>",
                                            "@type": "geosparql:gmlliteral"
                                            }
                                            }
            elif datatypes_dict.get(i[2]) == "lijnstring":
                result_dict[f'{i[0]}'] = {"@type": "lijnstring",
                                          "Geometrie.gml": {
                                            "@value": "<gml:Polyline srsName=\"http:\\//www.opengis.net/def/crs/EPSG/0/4326\"><gml:coordinates> Vul in: Lat Lon, Lat Lon</gml:coordinates><gml:Point>",
                                            "@type": "geosparql:gmlliteral"
                                            }
                                            }
            elif datatypes_dict.get(i[2]) == "DateTime":
                result_dict[f'{i[0]}'] = {"@type": "time:Instant",
                                        "time:inXSDDateTime": {
                                        "@type": "xml-schema:dateTime",
                                        "@value": "Vul in: YYYY-MM-DDThh:mm:ss"
                                        }}
            elif types_dict[range_id] == "Identificator":
                result_dict[f'{i[0]}'] =  {
                            "@type": "Identificator",
                            "Identificator.identificator": {
                            "@value": class_name+"_type001",
                            "@type": "cl-idt:"+class_name
                            }
                            }
            elif datatypes_dict.get(i[2]) in datatypes_yellow:
                result_dict[f'{i[0]}'] = datatypes_dict.get(i[2])
            else:
                result_dict[f'{i[0]}'] = datatypes_dict.get(i[2])

    def format_to_jsonld_structure_with_correct_id_and_refs(data, attributes_data, classes_data, datatypes, referencedEntities):
        jsonld_structure = []
        
        #create a dictionary with all the datatypes
        datatypes_dict = create_datatypes_dict(datatypes)
        referencedEntities_dict = create_datatypes_dict(referencedEntities)
        types_dict = {**datatypes_dict, **referencedEntities_dict}
        
        # Creating a mapping from class ID to its original ID
        class_id_to_original_id = {
            class_item['@id']: class_item['@id']
            for class_item in classes_data
        }
        
        # Creating a mapping from class names to their formatted IDs
        class_name_to_formatted_id = {
            next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), ''): "_:" + next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), '') + "001"
            for class_item in classes_data
        }
        
        # Creating a mapping from class names to their formatted IDs
        class_name_to_original_id = {
            next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), ''): class_item.get('@id')
            for class_item in classes_data
        }
        
        class_name_to_assigned_URI = {
            next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), ''): class_item.get('assignedURI')
            for class_item in classes_data
        }
        
        class_name_to_scope = {
            next((label['@value'] for label in class_item.get('vocLabel', []) if label.get('@language') == 'nl'), ''): class_item.get('scope')
            for class_item in classes_data
        }

        # Creating a mapping of property names to their range IDs
        property_name_to_range_id = {
            attr.get('vocLabel', [{}])[0].get('@value'): attr.get('range', {}).get('@id')
            for attr in attributes_data
        }
        
        # Creating a mapping of property names to their range IDs
        property_name_to_domain_id = {
            attr.get('vocLabel', [{}])[0].get('@value'): attr.get('domain', {}).get('@id')
            for attr in attributes_data
        }
        relations_dict = filter_properties_by_range(property_name_to_range_id, types_dict)

        domain_dict_attr = extract_range_domain_from_attributes(attributes_data)
        
        #datatypes_yellow is een dictionary van alle dataTypes op de UML

        def combine_dicts(d1, d2):
            datatypes_yellow = {}
            for key1, value1 in d1.items():
                for key2, value2 in d2.items():
                    if key1 == value2[0]:
                        if value1 not in datatypes_yellow:
                            datatypes_yellow[value1] = []
                        datatypes_yellow[value1].append((key2, value2[0], value2[1]))
            return datatypes_yellow
        datatypes_yellow = combine_dicts(datatypes_dict, domain_dict_attr)
        
        
        relation_dict = {key: [property_name_to_domain_id.get(key), relations_dict.get(key)] for key in property_name_to_domain_id}

        class_dict = {class_name_to_original_id[key]: [key, class_name_to_formatted_id.get(key), class_name_to_assigned_URI.get(key), class_name_to_scope.get(key)] for key in class_name_to_original_id}

        

        # Het resultaat zal een dictionary zijn met "@id" als sleutels en de rest van de data als sub-dictionary

        # Het resultaat zal een dictionary zijn met "@id" als sleutels en de rest van de data als sub-dictionary
        class_dict2 = {}
        attributes_dict = {}
        link_dict = {}

        # CREATE class_dict2
        for class_element in classes_data:
            if "@id" in class_element:
                current_id = class_element["@id"]
                class_dict2[current_id] = {}

                for key, value in class_element.items():
                    if key != "@id":                          
                        # Check of de waarde een lijst van dictionaries is
                        if isinstance(value, list) and value and isinstance(value[0], dict) and "@language" in value[0]:
                            # Zoek naar de dictionary met "@language": language
                            nl_value = next((item["@value"] for item in value if item.get("@language") == language), None)
                            if nl_value:
                                class_dict2[current_id][key] = nl_value
                                if key == "vocLabel":
                                    class_dict2[current_id]["blank_node"] = "_:"+nl_value+"001"
                        else:
                            class_dict2[current_id][key] = value

                    if "scope" not in class_dict2[current_id]:
                        class_dict2[current_id]["inherited_class"] = "yes"
                    else:
                        class_dict2[current_id]["inherited_class"] = "no"

                    if class_dict2[current_id].get("assignedURI") == "http://www.w3.org/2004/02/skos/core#Concept":
                        class_dict2[current_id]["codelijst"] = "yes"


        # CREATE class_dict2
        for class_element in attributes_data:
            if "@id" in class_element:
                current_id = class_element["@id"]
                if 'range' in class_element:
                        link_dict[current_id] = {} 

                for key, value in class_element.items():
                    if key == 'range':                    
                        # Check of de waarde een lijst van dictionaries is
                        if isinstance(value, list) and value and isinstance(value[0], dict) and "@language" in value[0]:
                            # Zoek naar de dictionary met "@language": language
                            nl_value = next((item["@value"] for item in value if item.get("@language") == language), None)
                            if nl_value:
                                link_dict[current_id][key] = nl_value
                                if key == "vocLabel":
                                    link_dict[current_id]["blank_node"] = "_:"+nl_value+"001"
                        else:
                            link_dict[current_id][key] = value["@id"]

        #print(link_dict)


                            
        # CREATE attributes_dict
        for attribute_element in attributes_data:
            if "@id" in attribute_element:
                current_id = attribute_element["@id"]
                attributes_dict[current_id] = {}

                for key, value in attribute_element.items():
                    if key != "@id":
                        # Check of de waarde een lijst van dictionaries is
                        if isinstance(value, list) and value and isinstance(value[0], dict) and "@language" in value[0]:
                            # Zoek naar de dictionary met "@language": language
                            nl_value = next((item["@value"] for item in value if item.get("@language") == language), None)
                            if nl_value:
                                attributes_dict[current_id][key] = nl_value
                        else:
                            attributes_dict[current_id][key] = value
        

        
        relation_dict2 = {property_name_to_domain_id[key]: [key, property_name_to_range_id.get(key)] for key in property_name_to_domain_id}
        #print(relation_dict)
        
        primary_id = find_value_for_key(class_name_to_original_id, start_class)
        
        orden_relations = reorder_dictionary_based_on_values(relation_dict, primary_id)
        #print(orden_relations)
        new_relation,remove_relations  = unique_dict(orden_relations)
        #print(new_relation)
        
        #print(remove_relations)
        
        relation_name = orden_relations
        
        
        # Vervang de tweede waarde in elke lijst van original_dict met de overeenkomstige waarde uit replacement_dict
        for key, value in relation_name.items():
            # Controleer of de waarde een lijst is met minimaal twee elementen
            if value[1] in class_dict:
                    value[1] = class_dict[value[1]][1]
        #print (attribute_element)
        
        for key, value in relation_name.items():
            if isinstance(value, list) and len(value) > 1:
                relation_name[key] = value[1]

        
        relation_name = {k: v for k, v in relation_name.items() if v is not None and not str(v).startswith("urn:")}
        for class_name, details in data.items():
            _id= details["id"]
            class_structure = {
                "@id": class_dict2[details["id"]].get("blank_node"),  # Ensuring "@id" is always formatted correctly
                "@type": class_name,
                #"id": class_id_to_original_id.get(details['id'], "UnknownID")  # Adding the original @id as "id"
                # Adding the original @id as "id"
            }

            
            if "parent" in class_dict2[_id]: #TODO: add property inherited from
                for parent in class_dict2[_id].get("parent"):
              
                    if class_dict2[parent["@id"]].get("inherited_class") == "yes":
                   
                        if class_dict2[parent["@id"]].get("vocLabel"):
                            class_structure["inherited_from"] = "Aanvullende properties kan je vinden in externe klasse : "+class_dict2[parent["@id"]].get("vocLabel")
                    else:
                        class_structure["parent"] = class_dict2[parent["@id"]].get("vocLabel")
                
            
            for property_name in details['properties']:
                property_name=to_camel_case(property_name)
                if '.' in property_name:
                    formatted_property_name = property_name.split('.')[1].strip()  # Extracting the actual property name
                else:
                    formatted_property_name = property_name.strip()
                
                formatted_property_name = to_camel_case(formatted_property_name)
                range_id = property_name_to_range_id.get(formatted_property_name)
                #print(property_name)
                full_class_name = class_name + "." + property_name
                # Setting the value to the corresponding class reference if exists
                if range_id and range_id in class_name_to_original_id:
                    if property_name in new_relation:
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = class_name_to_original_id.get(range_id, "")
                    else:
                        continue
                elif property_name in relation_name and property_name not in remove_relations:
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = relation_name[property_name] #TODO:PAS AAN
                elif range_id in types_dict:
                    if types_dict[range_id] == "TaalString" or types_dict[range_id] == "LangString":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = {"@language": "nl", "@value": "PAS AAN: vul "+property_name +" in"}
                    elif types_dict[range_id] == "String":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = "PAS AAN: vul "+property_name +" in"
                    elif types_dict[range_id] == "URI":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = "PAS AAN: vul URI in"
                    elif types_dict[range_id] == "DateTime":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = {"@type": "time:Instant",
                                                "time:inXSDDateTime": {
                                                "@type": "xml-schema:dateTime",
                                                "@value": "Vul in: YYYY-MM-DDThh:mm:ss"
                                                }}
                    elif types_dict[range_id] == "punt":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = {"@type": "punt",
                                                "Geometrie.gml": {
                                                    "@value": "<gml:Point srsName=\"http:\\//www.opengis.net/def/crs/EPSG/0/4326\"><gml:coordinates>  Vul in: Lat Lon </gml:coordinates><gml:Point>",
                                                    "@type": "geosparql:gmlliteral"
                                                    }
                                                    }
                    elif types_dict[range_id] == "lijnstring":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] = {"@type": "lijnstring",
                                                "Geometrie.gml": {
                                                    "@value": "<gml:Polyline srsName=\"http:\\//www.opengis.net/def/crs/EPSG/0/4326\"><gml:coordinates> Vul in: Lat Lon, Lat Lon</gml:coordinates><gml:Point>",
                                                    "@type": "geosparql:gmlliteral"
                                                    }
                                                    }
                    elif types_dict[range_id] == "Identificator":
                        class_dict["properties"] = "yes"
                        class_structure[full_class_name] =  {
                                "@type": "Identificator",
                                "Identificator.identificator": {
                                "@value": class_name+"_type001",
                                "@type": "cl-idt:"+class_name
                                }
                                }
                    else:

                        if types_dict[range_id] in datatypes_yellow:
                            values_datatypes_yellow = get_first_elements(datatypes_yellow.get(types_dict[range_id]))
                            values_datatypes_yellow_domein = get_second_elements(datatypes_yellow.get(types_dict[range_id]))
                            result_dict = {"@type": types_dict[range_id]}
                            
                            loop_datatypes(datatypes_dict, result_dict, datatypes_yellow, types_dict,range_id, class_name)
                            class_structure[full_class_name] = result_dict
                        else:
                            if types_dict[range_id] == "TaalString":

                                class_structure[full_class_name] = {"@language": "nl", "@value": "PAS AAN: vul "+property_name +" in"}
                            elif types_dict[range_id] == "String":

                                class_structure[full_class_name] = "PAS AAN: vul "+property_name +" in"
                            class_structure[full_class_name] = types_dict[range_id]
                            
                else:
                    if property_name in relation_dict and relation_dict.get(property_name)[1] in class_dict : 
                        if class_dict2.get(relation_dict.get(property_name)[1])['assignedURI'] == "http://www.w3.org/2004/02/skos/core#Concept":
                            class_structure[full_class_name] = "cl-" + class_dict.get(relation_dict.get(property_name)[1])[0] + "#Vul_in"
                        else:
                            class_structure[full_class_name] = class_dict.get(relation_dict.get(property_name)[1])[1]
                    else:
                        if property_name not in remove_relations:
                            class_structure[property_name] = ""
            if class_dict2.get(data[class_name].get('id'))['assignedURI'] == "http://www.w3.org/2004/02/skos/core#Concept":
                    continue
            elif class_name_to_scope.get(class_name) is None:
                continue
            else:
                jsonld_structure.append(class_structure)

        return jsonld_structure


    def find_children(classes, start_id):
        """
        Find all children of a class starting from the '@id' of that class.
        Children are identified by having the '@id' of the starting class in their 'parent' key.

        :param classes: List of dictionaries representing classes.
        :param start_id: The '@id' of the class to start from.
        :return: A list of '@id's of all children classes.
        """
        def find_children_recursive(current_id, classes, found_children):
            for cls in classes:
                # Check if this class has a parent and if the current id is one of its parents
                if 'parent' in cls and any(parent.get('@id') == current_id for parent in cls['parent']):
                    child_id = cls['@id']
                    if child_id not in found_children:
                        found_children.append(child_id)
                        find_children_recursive(child_id, classes, found_children)

        children_ids = []
        find_children_recursive(start_id, classes, children_ids)
        return children_ids



    # Find children starting from a given '@id'
    start_class_id = 'urn:oslo-toolchain:684a44dc0aa851133f2f91069da75e2dd4816d4b17de846a1a3797c8df66e947'



    
    
    # File paths
    input_file_path = name + '.jsonld'
    output_file_path = name + '_example.jsonld'
    language = 'nl'

    # Reading the JSON-LD file
    jsonld_data = read_jsonld_file(input_file_path)


    # Extracting classes and properties
    extracted_data, attributes_data = extract_classes_and_properties_from_jsonld(jsonld_data)

    # Formatting to JSON-LD structure with correct "@id" and class references
    jsonld_formatted_data = format_to_jsonld_structure_with_correct_id_and_refs(extracted_data, attributes_data, jsonld_data['classes'], jsonld_data['datatypes'], jsonld_data['referencedEntities'])

    # Updated script to process the new data
    context = []

    for item in jsonld_data['classes']:
        if item.get('assignedURI') == 'http://www.w3.org/2004/02/skos/core#Concept':
            diagram_labels = item.get('diagramLabel', [])
            for label in diagram_labels:
                value = label.get('@value')
                if value:
                    context_entry = {"cl-{}".format(value): "https://data.vlaanderen.be/doc/concept/{}#".format(value)}
                    context.append(context_entry)
    context = {k: v for d in context for k, v in d.items()}

    children = find_children(jsonld_data['classes'], start_class_id)
    print(children)
    
    
    # Create JSON-LD with the provided context
    final_jsonld_data = create_jsonld_with_context(jsonld_formatted_data, context)


    # Writing the extracted data to a new JSON-LD file
    write_to_jsonld_file(final_jsonld_data, output_file_path)




if __name__ == "__main__":
    main()
