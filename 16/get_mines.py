from openmindat import LocalitiesRetriever

retriever = LocalitiesRetriever()

# MineralSitesRetriever no longer exists; LocalitiesRetriever is the equivalent.
# bbox filtering is not supported by this library — filter by lat/lon in post-processing if needed.
# Output is always JSON (GeoJSON format is not supported by the library).
retriever.country("Papua New Guinea").saveto("output/")
