from beacon.conf import conf

#### PLEASE, ALL THE HANDOVERS YOU NEED FOR BEACON TO SHOW LIKE THE handover_1 EXAMPLE BELOW #####

handover_1={
    "note": "Description of the handover",
    "url": conf.uri,
    "handoverType": {
                    'id': 'NCIT:C189151',
                    'label': 'Study Data Repository'
                }
}

#### PLEASE, ADD THE HANDOVER VARIABLES FROM ABOVE YOU WANT TO ADD TO BEACON TO THE list_of_handovers VARIABLE BELOW #####
list_of_handovers=[handover_1]


#### PLEASE, ALL THE HANDOVERS PER DATASET YOU NEED FOR BEACON TO SHOW LIKE THE dataset1_handover EXAMPLE BELOW #####


dataset1_id='test' # This has to match the id for the dataset

dataset1_handover={"dataset": dataset1_id, "handover": handover_1}


#### PLEASE, ADD THE HANDOVER PER DATASET VARIABLES FROM ABOVE YOU WANT TO ADD TO BEACON TO THE list_of_handovers_per_dataset VARIABLE BELOW #####

list_of_handovers_per_dataset=[dataset1_handover]