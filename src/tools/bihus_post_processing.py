import os
import json
from fuzzywuzzy import fuzz
import spacy
from tqdm import tqdm

class IdentityIdentifier:
    def __init__(self, input_dir, output_dir, model_name="uk_core_news_sm"):
        """
        Initialize the IdentityIdentifier.

        :param input_dir: Path to the folder containing JSON files.
        :param output_dir: Path to the folder to save modified JSON files.
        :param model_name: Name of the spaCy model to use.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.nlp = spacy.load(model_name)

    def extract_entities(self, content):
        """Extract all entities grouped by their labels."""
        doc = self.nlp(content)
        entities = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text)
        return entities

    def merge_variants(self, entities):
        """Merge entity variants for all entity types."""
        merged_entities = {}
        for label, entity_list in entities.items():
            unique_entities = []
            for entity in entity_list:
                is_variant = False
                for unique_entity in unique_entities:
                    if fuzz.ratio(entity, unique_entity) > 80:  # Threshold for merging
                        is_variant = True
                        break
                if not is_variant:
                    unique_entities.append(entity)
            merged_entities[label] = unique_entities
        return merged_entities

    def process_article(self, article):
        """Process a single article to extract and merge entities."""
        content = article.get("content", "")
        raw_entities = self.extract_entities(content)
        merged_entities = self.merge_variants(raw_entities)
        article["entities_included"] = merged_entities
        return article

    def process_all_jsons(self):
        """Process all JSON files in the input folder and save them to the output folder."""
        for file in tqdm(os.listdir(self.input_dir), desc="Processing JSON files", unit="file", total=len(os.listdir(self.input_dir))):
            if file.endswith(".json"):
                input_path = os.path.join(self.input_dir, file)
                output_path = os.path.join(self.output_dir, file)
                with open(input_path, "r", encoding="utf-8") as f:
                    article = json.load(f)
                modified_article = self.process_article(article)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(modified_article, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    input_dir = "./bihus_parsed_data"
    output_dir = "./bihus_modified_identity_data"
    identifier = IdentityIdentifier(input_dir, output_dir)
    identifier.process_all_jsons()
