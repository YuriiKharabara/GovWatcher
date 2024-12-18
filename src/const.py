SCRAPING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "politician_name": {"type": "string", "description": "Name of the politician"},
        "politician_surname": {"type": "string", "description": "Surname of the politician"},
        "type_dec": {"type": "string", "description": "Type of declaration"},
        "year": {"type": "string", "description": "Year of the declaration"},
        "registration_place": {"type": "string", "description": "Registration place of the politician"},
        "place_of_work": {"type": "string", "description": "Place of work of the politician"},
        "position_held": {"type": "string", "description": "Position held by the politician"},
        "family_members": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "connection": {"type": "string", "description": "Connection to the politician"},
                    "name": {"type": "string", "description": "Name of the family member"},
                    "surname": {"type": "string", "description": "Surname of the family member"},
                    "nationality": {"type": "string", "description": "Nationality of the family member"}
                },
                "required": ["connection", "name", "surname", "nationality"],
                "additionalProperties": False  # Added
            },
            "description": "List of family members of the politician"
        },
        "real_estate": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {"type": "number", "description": "Area of the real estate"},
                    "location": {"type": "string", "description": "Location of the real estate"},
                    "price": {"type": "number", "description": "Price of the real estate"},
                    "currency": {"type": "string", "description": "Currency of the price"}
                },
                "required": ["area", "location", "price", "currency"],
                "additionalProperties": False,  # Added
                "description": "List of real estate owned by the politician"
            }
        },
        "vehicles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model": {"type": "string", "description": "Model of the vehicle"},
                    "price": {"type": "number", "description": "Price of the vehicle"},
                    "currency": {"type": "string", "description": "Currency of the price"}
                },
                "required": ["model", "price", "currency"],
                "additionalProperties": False  # Added
            },
            "description": "List of vehicles owned by the politician"
        },
        "financial_data": {
            "type": "object",
            "properties": {
                "income_including_gifts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source of the income"},
                            "type": {"type": "string", "description": "Type of the income"},
                            "amount": {"type": "number", "description": "Amount of the income"},
                            "currency": {"type": "string", "description": "Currency of the income"}
                        },
                        "required": ["source", "type", "amount", "currency"],
                        "additionalProperties": False,  # Added
                        "description": "Income including gifts of the politician"
                    }
                },
                "assets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "description": "Type of the asset"},
                            "amount": {"type": "number", "description": "Amount of the asset"},
                            "currency": {"type": "string", "description": "Currency of the asset"}
                        },
                        "required": ["type", "amount", "currency"],
                        "additionalProperties": False  # Added
                    },
                    "description": "Assets of the politician"
                }
            },
            "required": ["income_including_gifts", "assets"],
            "additionalProperties": False,  # Added
            "description": "Financial data of the politician"
        }
    },
    "required": [
        "type_dec", "year", "registration_place", "place_of_work",
        "position_held", "family_members", "real_estate", "vehicles", "financial_data", "politician_name", "politician_surname"
    ],
    "additionalProperties": False  # Added
}

SCRAPING_PROMPT = "You are an expert at structured data extraction of declarations and law information. \
You will be given unstructured text from a html response and should convert it into the given structure."

DECLARATIONS_ANALYSIS_PROMPT = """
You are an analyst tasked with evaluating a politician’s declarations data for potential corruption indicators. \
You have the following JSON array of declarations (each object is a separate declaration for the same politician):

###
{declarations_data}
###

Please analyze these declarations and determine:

1. Presence of large gifts.
2. Sudden change in declared cash/money in accounts.
3. Discrepancy between income and property, using the scale 0 to 2:
   - 0: still acceptable,
   - 1: suspicious (it would have taken a long time to save money),
   - 2: unrealistic to accumulate with such salary/income.
   Note: Some real estate can be declared with 0 price, it should be ignored.

Pay attention to the chronological order of the declarations.
"""

DECLARATIONS_ANALYSIS_RESPONSE_SCHEMA = {
    "type": "object",
    "title": "CorruptionIndicators",
    "description": "Schema for detecting potential corruption indicators in politician's declarations",
    "properties": {
        "presence_of_large_gifts": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "boolean",
                    "description": "Indicates if large gifts are present."
                },
                "explanation": {
                    "type": "string",
                    "description": "A brief explanation of why this value was assigned."
                },
                "references": {
                    "type": "array",
                    "description": "List of direct references to declarations supporting this conclusion.",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["value", "explanation", "references"],
            "additionalProperties": False
        },
        "sudden_changes_in_declared_money": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "boolean",
                    "description": "Indicates if sudden changes in declared money are present."
                },
                "explanation": {
                    "type": "string",
                    "description": "A brief explanation of why this value was assigned."
                },
                "references": {
                    "type": "array",
                    "description": "List of direct references to declarations indicating sudden changes.",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["value", "explanation", "references"],
            "additionalProperties": False
        },
        "discrepancy_between_income_and_property": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "integer",
                    "description": "Scale (0, 1, or 2) indicating discrepancy severity."
                },
                "explanation": {
                    "type": "string",
                    "description": "A brief explanation of why this value was assigned."
                },
                "references": {
                    "type": "array",
                    "description": "List of direct references to declarations illustrating the property-income mismatch.",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["value", "explanation", "references"],
            "additionalProperties": False
        }
    },
    "required": [
        "presence_of_large_gifts",
        "sudden_changes_in_declared_money",
        "discrepancy_between_income_and_property"
    ],
    "additionalProperties": False
}
