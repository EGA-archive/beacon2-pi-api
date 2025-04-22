from beacon.source.entry_types import analysis, biosample, cohort, dataset, individual, genomicVariant, run
from beacon.source.manage import analyses, biosamples, cohorts, datasets, individuals, g_variants, runs
from beacon.source.map_entry_types import map_analysis, analysis_single, analysis_genomicVariant, map_biosample, biosample_analysis, biosample_genomicVariant, biosample_run, biosample_single, map_cohort, cohort_analysis, cohort_individual, cohort_run, cohort_single, map_dataset, dataset_analysis, dataset_biosample, dataset_genomicVariant, dataset_individual, dataset_run, dataset_single, map_individual, individual_analysis, individual_biosample, individual_genomicVariant, individual_run, individual_single, map_run, run_analysis, run_genomicVariant, run_single, map_genomicVariant, genomicVariant_analysis, genomicVariant_biosample, genomicVariant_individual, genomicVariant_run, genomicVariant_single
from beacon.request.classes import ErrorClass

def get_entry_types(self):
    try:
        entry_types={}
        entry_types["entryTypes"]={}
        if analyses["granularity"]["boolean"]==True or analyses["granularity"]["count"]==True or analyses["granularity"]["record"]==True:
            entry_types["entryTypes"]["analysis"]=analysis# pragma: no cover
        if biosamples["granularity"]["boolean"]==True or biosamples["granularity"]["count"]==True or biosamples["granularity"]["record"]==True:
            entry_types["entryTypes"]["biosample"]=biosample# pragma: no cover
        if cohorts["granularity"]["boolean"]==True or cohorts["granularity"]["count"]==True or cohorts["granularity"]["record"]==True:
            entry_types["entryTypes"]["cohort"]=cohort# pragma: no cover
        if datasets["granularity"]["boolean"]==True or datasets["granularity"]["count"]==True or datasets["granularity"]["record"]==True:
            entry_types["entryTypes"]["dataset"]=dataset
        if g_variants["granularity"]["boolean"]==True or g_variants["granularity"]["count"]==True or g_variants["granularity"]["record"]==True:
            entry_types["entryTypes"]["genomicVariant"]=genomicVariant
        if individuals["granularity"]["boolean"]==True or individuals["granularity"]["count"]==True or individuals["granularity"]["record"]==True:
            entry_types["entryTypes"]["individual"]=individual# pragma: no cover
        if runs["granularity"]["boolean"]==True or runs["granularity"]["count"]==True or runs["granularity"]["record"]==True:
            entry_types["entryTypes"]["run"]=run# pragma: no cover
        return entry_types
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

def get_entry_types_map(self):
    try:
        map_entry_types={}
        map_entry_types["endpointSets"]={}
        if analyses["granularity"]["boolean"]==True or analyses["granularity"]["count"]==True or analyses["granularity"]["record"]==True:# pragma: no cover
            analyses_endpoints={}
            if analyses["singleEntryUrl"]==True:
                map_analysis["singleEntryUrl"]=analysis_single
            if analyses["endpoints"]["genomicVariant"]==True:
                analyses_endpoints["genomicVariant"]=analysis_genomicVariant
                map_analysis["endpoints"]={}
                map_analysis["endpoints"]=analyses_endpoints
            map_entry_types["endpointSets"]["analysis"]=map_analysis
        if biosamples["granularity"]["boolean"]==True or biosamples["granularity"]["count"]==True or biosamples["granularity"]["record"]==True:# pragma: no cover
            biosamples_endpoints={}
            if biosamples["singleEntryUrl"]==True:
                map_biosample["singleEntryUrl"]=biosample_single
            if biosamples["endpoints"]["genomicVariant"]==True:
                biosamples_endpoints["genomicVariant"]=biosample_genomicVariant
                try:
                    map_biosample["endpoints"]["genomicVariant"]=biosamples_endpoints
                except Exception:
                    map_biosample["endpoints"]={}
                    map_biosample["endpoints"]=biosamples_endpoints
            if biosamples["endpoints"]["analysis"]==True:
                biosamples_endpoints["analysis"]=biosample_analysis
                try:
                    map_biosample["endpoints"]=biosamples_endpoints
                except Exception:
                    map_biosample["endpoints"]={}
                    map_biosample["endpoints"]=biosamples_endpoints
            if biosamples["endpoints"]["run"]==True:
                biosamples_endpoints["run"]=biosample_run
                try:
                    map_biosample["endpoints"]=biosamples_endpoints
                except Exception:
                    map_biosample["endpoints"]={}
                    map_biosample["endpoints"]=biosamples_endpoints
            map_entry_types["endpointSets"]["biosample"]=map_biosample
        if cohorts["granularity"]["boolean"]==True or cohorts["granularity"]["count"]==True or cohorts["granularity"]["record"]==True:# pragma: no cover
            cohorts_endpoints={}
            if cohorts["singleEntryUrl"]==True:
                map_cohort["singleEntryUrl"]=cohort_single
            if cohorts["endpoints"]["individual"]==True:
                cohorts_endpoints["individual"]=cohort_individual
                try:
                    map_cohort["endpoints"]=cohorts_endpoints
                except Exception:
                    map_cohort["endpoints"]={}
                    map_cohort["endpoints"]=cohorts_endpoints
            if cohorts["endpoints"]["analysis"]==True:
                cohorts_endpoints["analysis"]=cohort_analysis
                try:
                    map_cohort["endpoints"]=cohorts_endpoints
                except Exception:
                    map_cohort["endpoints"]={}
                    map_cohort["endpoints"]=cohorts_endpoints
            if cohorts["endpoints"]["run"]==True:
                cohorts_endpoints["run"]=cohort_run
                try:
                    map_cohort["endpoints"]=cohorts_endpoints
                except Exception:
                    map_cohort["endpoints"]={}
                    map_cohort["endpoints"]=cohorts_endpoints
            map_entry_types["endpointSets"]["cohort"]=map_cohort
        if datasets["granularity"]["boolean"]==True or datasets["granularity"]["count"]==True or datasets["granularity"]["record"]==True:
            datasets_endpoints={}
            if datasets["singleEntryUrl"]==True:
                map_dataset["singleEntryUrl"]=dataset_single# pragma: no cover
            if datasets["endpoints"]["individual"]==True:# pragma: no cover
                datasets_endpoints["individual"]=dataset_individual
                try:
                    map_dataset["endpoints"]=datasets_endpoints
                except Exception:
                    map_dataset["endpoints"]={}
                    map_dataset["endpoints"]=datasets_endpoints
            if datasets["endpoints"]["analysis"]==True:# pragma: no cover
                datasets_endpoints["analysis"]=dataset_analysis
                try:
                    map_dataset["endpoints"]=datasets_endpoints
                except Exception:
                    map_dataset["endpoints"]={}
                    map_dataset["endpoints"]=datasets_endpoints
            if datasets["endpoints"]["run"]==True:# pragma: no cover
                datasets_endpoints["run"]=dataset_run
                try:
                    map_dataset["endpoints"]=datasets_endpoints
                except Exception:
                    map_dataset["endpoints"]={}
                    map_dataset["endpoints"]=datasets_endpoints
            if datasets["endpoints"]["biosample"]==True:# pragma: no cover
                datasets_endpoints["biosample"]=dataset_biosample
                try:
                    map_dataset["endpoints"]=datasets_endpoints
                except Exception:
                    map_dataset["endpoints"]={}
                    map_dataset["endpoints"]=datasets_endpoints
            if datasets["endpoints"]["genomicVariant"]==True:# pragma: no cover
                datasets_endpoints["genomicVariant"]=dataset_genomicVariant
                try:
                    map_dataset["endpoints"]=datasets_endpoints
                except Exception:
                    map_dataset["endpoints"]={}
                    map_dataset["endpoints"]=datasets_endpoints
            map_entry_types["endpointSets"]["dataset"]=map_dataset
        if g_variants["granularity"]["boolean"]==True or g_variants["granularity"]["count"]==True or g_variants["granularity"]["record"]==True:
            g_variants_endpoints={}
            if g_variants["singleEntryUrl"]==True:# pragma: no cover
                map_genomicVariant["singleEntryUrl"]=genomicVariant_single
            if g_variants["endpoints"]["individual"]==True:# pragma: no cover
                g_variants_endpoints["individual"]=genomicVariant_individual
                try:
                    map_genomicVariant["endpoints"]=g_variants_endpoints
                except Exception:
                    map_genomicVariant["endpoints"]={}
                    map_genomicVariant["endpoints"]=g_variants_endpoints
            if g_variants["endpoints"]["analysis"]==True:# pragma: no cover
                g_variants_endpoints["analysis"]=genomicVariant_analysis
                try:
                    map_genomicVariant["endpoints"]=g_variants_endpoints
                except Exception:
                    map_genomicVariant["endpoints"]={}
                    map_genomicVariant["endpoints"]=g_variants_endpoints
            if g_variants["endpoints"]["run"]==True:# pragma: no cover
                g_variants_endpoints["run"]=genomicVariant_run
                try:
                    map_genomicVariant["endpoints"]=g_variants_endpoints
                except Exception:
                    map_genomicVariant["endpoints"]={}
                    map_genomicVariant["endpoints"]=g_variants_endpoints
            if g_variants["endpoints"]["biosample"]==True:# pragma: no cover
                g_variants_endpoints["biosample"]=genomicVariant_biosample
                try:
                    map_genomicVariant["endpoints"]=g_variants_endpoints
                except Exception:
                    map_genomicVariant["endpoints"]={}
                    map_genomicVariant["endpoints"]=g_variants_endpoints
            map_entry_types["endpointSets"]["genomicVariant"]=map_genomicVariant
        if individuals["granularity"]["boolean"]==True or individuals["granularity"]["count"]==True or individuals["granularity"]["record"]==True:# pragma: no cover
            individuals_endpoints={}
            if individuals["singleEntryUrl"]==True:
                map_individual["singleEntryUrl"]=individual_single
            if individuals["endpoints"]["genomicVariant"]==True:
                individuals_endpoints["genomicVariant"]=individual_genomicVariant
                try:
                    map_individual["endpoints"]=individuals_endpoints
                except Exception:
                    map_individual["endpoints"]={}
                    map_individual["endpoints"]=individuals_endpoints
            if individuals["endpoints"]["analysis"]==True:
                individuals_endpoints["analysis"]=individual_analysis
                try:
                    map_individual["endpoints"]=individuals_endpoints
                except Exception:
                    map_individual["endpoints"]={}
                    map_individual["endpoints"]=individuals_endpoints
            if individuals["endpoints"]["run"]==True:
                individuals_endpoints["run"]=individual_run
                try:
                    map_individual["endpoints"]=individuals_endpoints
                except Exception:
                    map_individual["endpoints"]={}
                    map_individual["endpoints"]=individuals_endpoints
            if individuals["endpoints"]["biosample"]==True:
                individuals_endpoints["biosample"]=individual_biosample
                try:
                    map_individual["endpoints"]=individuals_endpoints
                except Exception:
                    map_individual["endpoints"]={}
                    map_individual["endpoints"]=individuals_endpoints
            map_entry_types["endpointSets"]["individual"]=map_individual
        if runs["granularity"]["boolean"]==True or runs["granularity"]["count"]==True or runs["granularity"]["record"]==True:# pragma: no cover
            runs_endpoints={}
            if runs["singleEntryUrl"]==True:
                map_run["singleEntryUrl"]=run_single
            if runs["endpoints"]["genomicVariant"]==True:
                runs_endpoints["genomicVariant"]=run_genomicVariant
                try:
                    map_run["endpoints"]=runs_endpoints
                except Exception:
                    map_run["endpoints"]={}
                    map_run["endpoints"]=runs_endpoints
            if runs["endpoints"]["analysis"]==True:
                runs_endpoints["analysis"]=run_analysis
                try:
                    map_run["endpoints"]=runs_endpoints
                except Exception:
                    map_run["endpoints"]={}
                    map_run["endpoints"]=runs_endpoints
            map_entry_types["endpointSets"]["run"]=map_run
        return map_entry_types
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise