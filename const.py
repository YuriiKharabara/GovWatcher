SCRAPING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "type_dec": {"type": "string"},
        "year": {"type": "string"},
        "registration_place": {"type": "string"},
        "place_of_work": {"type": "string"},
        "position_held": {"type": "string"},
        "family_members": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "connection": {"type": "string"},
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                    "nationality": {"type": "string"}
                },
                "required": ["connection", "name", "surname", "nationality"],
                "additionalProperties": False  # Added
            }
        },
        "real_estate": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {"type": "number"},
                    "location": {"type": "string"},
                    "price": {"type": "number"},
                    "currency": {"type": "string"}
                },
                "required": ["area", "location", "price", "currency"],
                "additionalProperties": False  # Added
            }
        },
        "vehicles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "price": {"type": "number"},
                    "currency": {"type": "string"}
                },
                "required": ["model", "price", "currency"],
                "additionalProperties": False  # Added
            }
        },
        "financial_data": {
            "type": "object",
            "properties": {
                "income_including_gifts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "type": {"type": "string"},
                            "amount": {"type": "number"},
                            "currency": {"type": "string"}
                        },
                        "required": ["source", "type", "amount", "currency"],
                        "additionalProperties": False  # Added
                    }
                },
                "assets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "amount": {"type": "number"},
                            "currency": {"type": "string"}
                        },
                        "required": ["type", "amount", "currency"],
                        "additionalProperties": False  # Added
                    }
                }
            },
            "required": ["income_including_gifts", "assets"],
            "additionalProperties": False  # Added
        }
    },
    "required": [
        "type_dec", "year", "registration_place", "place_of_work",
        "position_held", "family_members", "real_estate", "vehicles", "financial_data"
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
