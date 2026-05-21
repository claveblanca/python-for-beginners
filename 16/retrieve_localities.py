from openmindat import LocalitiesRetriever

# Retrieve gold (Au) mine localities in Papua New Guinea
lr = LocalitiesRetriever()
lr.country("Papua New Guinea").elements_inc("Au")
lr.saveto("mindat_data")

