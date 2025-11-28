from beacon.conf import conf

#### Please, all the handovers you need for beacon to show like the handover_1 example below #####

handover_1={
    "note": "Description of the handover",
    "url": conf.uri,
    "handoverType": {
                    'id': 'NCIT:C189151',
                    'label': 'Study Data Repository'
                }
}

#### Please, add the handover variables from above you want to add to beacon to the list_of_handovers variable below #####
list_of_handovers=[handover_1]


#### Please, all the handovers per dataset you need for beacon to show like the dataset1_handover example below #####


dataset1_id='test' # This has to match the id for the dataset

dataset1_handover={"dataset": dataset1_id, "handover": handover_1}


#### Please, add the handover per dataset variables from above you want to add to beacon to the list_of_handovers_per_dataset variable below #####

list_of_handovers_per_dataset=[dataset1_handover]