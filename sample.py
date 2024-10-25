import arcmapper

arc = arcmapper.read_arc_schema("1.0.0")
dd = arcmapper.read_data_dictionary(
    "ccpuk.csv",
    description_field="Field Label",
    response_field="Choices, Calculations, OR Slider Labels",
    response_func="redcap",
)
print("Mapping using TF-IDF... ", end="")
arcmapper.map("tf-idf", dd, arc).to_csv("mapping_tfidf.csv", index=False)
print("done.")
print(" Mapping using SBERT... ", end="")
arcmapper.map("sbert", dd, arc).to_csv("mapping_sbert.csv", index=False)
print("done.")
