import pandas as pd

from arcmapper.dictionary import read_from_jsonschema


EXAMPLE_JSON_SCHEMA = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["option1", "option2", "option3"],
      "description": "category of the variable"
    },
    "value": {
      "type": "number",
      "description": "default value of variable"
    },
    "full_name": {
      "type": "string",
      "description": "full name of variable"
    }
  },
  "required": ["category", "value", "full_name"]
}"""

def test_read_data_dictionary(data_dictionary):
    assert data_dictionary.columns.tolist()== ["variable", "description", "responses", "type"]


def test_read_from_jsonschema():
    dd = read_from_jsonschema(EXAMPLE_JSON_SCHEMA)
    print(dd)
    expected = pd.DataFrame({'variable': ["category", "value", "full_name"],
                             'description': ['category of the variable', 'default value of variable', 'full name of variable'],
                             'responses': [[('option1', 'option1'),('option2', 'option2'),('option3', 'option3')], None, None],
                             'type': ['categorical', 'number', 'string']})
    assert dd.equals(expected)

