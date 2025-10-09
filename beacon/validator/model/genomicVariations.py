import re
import argparse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)

from typing import Optional, Union

class OntologyTerm(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class Members(BaseModel, extra='forbid'):
    affected: bool
    memberId: str
    role: OntologyTerm

class Reference(BaseModel, extra='forbid'):
    id: Optional[str] = None
    notes: Optional[str] = None
    reference: Optional[str] = None

class Number(BaseModel, extra='forbid'):
    type: str
    value: int
    @field_validator('type')
    @classmethod
    def type_must_be_Number(cls, v: str) -> str:
        if v == 'Number':
            pass
        else:
            raise ValueError('type can only contain the word Number')
        return v.title()

class DefiniteRange(BaseModel, extra='forbid'):
    type: str
    min: Union[int, float]
    max: Union[int, float]
    @field_validator('type')
    @classmethod
    def type_must_be_DefiniteRange(cls, v: str) -> str:
        if v == 'DefiniteRange':
            pass
        else:
            raise ValueError('type can only contain the word DefiniteRange')
        return v.title()
    
class IndefiniteRange(BaseModel, extra='forbid'):
    type: str
    value: Union[int, float]
    comparator: str
    @field_validator('type')
    @classmethod
    def type_must_be_IndefiniteRange(cls, v: str) -> str:
        if v == 'IndefiniteRange':
            pass
        else:
            raise ValueError('type can only contain the word IndefiniteRange')
        return v.title()
    @field_validator('comparator')
    @classmethod
    def comparator_options(cls, v: str) -> str:
        if v in ["<=",">="]:
            pass
        else:
            raise ValueError('comparator must be <= or >=')
        return v.title()

class CytobandInterval(BaseModel, extra='forbid'):
    type: str
    start: str
    end: str
    @field_validator('type')
    @classmethod
    def type_must_be_CytobandInterval(cls, v: str) -> str:
        if v == 'CytobandInterval':
            pass
        else:
            raise ValueError('type can only contain the word CytobandInterval')
        return v.title()
    @field_validator('start')
    @classmethod
    def start_must_be_HumanCytoband(cls, v: str) -> str:
        if re.match("^cen|[pq](ter|([1-9][0-9]*(\\.[1-9][0-9]*)?))$", v):
            pass
        else:
            raise ValueError('start must be a character string representing cytobands derived from the *International System for Human Cytogenomic Nomenclature* (ISCN)')
        return v.title()
    @field_validator('end')
    @classmethod
    def end_must_be_HumanCytoband(cls, v: str) -> str:
        if re.match("^cen|[pq](ter|([1-9][0-9]*(\\.[1-9][0-9]*)?))$", v):
            pass
        else:
            raise ValueError('end must be a character string representing cytobands derived from the *International System for Human Cytogenomic Nomenclature* (ISCN)')
        return v.title()

class SimpleInterval(BaseModel, extra='forbid'):
    type: str
    start: int
    end: int
    @field_validator('type')
    @classmethod
    def type_must_be_SimpleInterval(cls, v: str) -> str:
        if v == 'SimpleInterval':
            pass
        else:
            raise ValueError('type can only contain the word SimpleInterval')
        return v.title()
    
class SequenceInterval(BaseModel, extra='forbid'):
    type: str
    start: Union[DefiniteRange, IndefiniteRange, Number]
    end: Union[DefiniteRange, IndefiniteRange, Number]
    @field_validator('type')
    @classmethod
    def type_must_be_SequenceInterval(cls, v: str) -> str:
        if v == 'SequenceInterval':
            pass
        else:
            raise ValueError('type can only contain the word SequenceInterval')
        return v.title()

class ChromosomeLocation(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    species_id: str
    chr: str
    interval: CytobandInterval
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_ChromosomeLocation(cls, v: str) -> str:
        if v == 'ChromosomeLocation':
            pass
        else:
            raise ValueError('type can only contain the word ChromosomeLocation')
        return v.title()
    @field_validator('species_id')
    @classmethod
    def species_id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('species_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('chr')
    @classmethod
    def chr_allowed(cls, v: str) -> str:
        list_chr= ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","X","Y"]
        if v in list_chr:
            pass
        else:
            raise ValueError('chr must be a valid chromosome, e.g. 1..22, X, Y')
        return v.title()
    
class SequenceLocation(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    sequence_id: str
    interval: Union[SequenceInterval,SimpleInterval]
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_SequenceLocation(cls, v: str) -> str:
        if v == 'SequenceLocation':
            pass
        else:
            raise ValueError('type can only contain the word SequenceLocation')
        return v.title()
    @field_validator('sequence_id')
    @classmethod
    def sequence_id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z_0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('sequence_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    
class DerivedSequenceExpression(BaseModel, extra='forbid'):
    type: str
    location: SequenceLocation
    reverse_complement: bool
    @field_validator('type')
    @classmethod
    def type_must_be_DerivedSequenceExpression(cls, v: str) -> str:
        if v == 'DerivedSequenceExpression':
            pass
        else:
            raise ValueError('type can only contain the word DerivedSequenceExpression')
        return v.title()
    
class LiteralSequenceExpression(BaseModel, extra='forbid'):
    type: str
    sequence: str
    @field_validator('type')
    @classmethod
    def type_must_be_LiteralSequenceExpression(cls, v: str) -> str:
        if v == 'LiteralSequenceExpression':
            pass
        else:
            raise ValueError('type can only contain the word LiteralSequenceExpression')
        return v.title()
    @field_validator('sequence')
    @classmethod
    def check_sequence(cls, v: str) -> str:
        if re.match("^[A-Z*\\-]*$", v):
            pass
        else:
            raise ValueError('sequence must be a character string of Residues that represents a biological sequence using the conventional sequence order (5’-to-3’ for nucleic acid sequences, and amino-to-carboxyl for amino acid sequences). IUPAC ambiguity codes are permitted in Sequences.')
        return v.title()
    
class RepeatedSequenceExpression(BaseModel, extra='forbid'):
    type: str
    seq_expr: Union[DerivedSequenceExpression, LiteralSequenceExpression]
    count: Union[DefiniteRange, IndefiniteRange, Number]
    @field_validator('type')
    @classmethod
    def type_must_be_RepeatedSequenceExpression(cls, v: str) -> str:
        if v == 'RepeatedSequenceExpression':
            pass
        else:
            raise ValueError('type can only contain the word RepeatedSequenceExpression')
        return v.title()
    
class ComposedSequenceExpression(BaseModel, extra='forbid'):
    type: Optional[str] = None
    components: list
    @field_validator('type')
    @classmethod
    def type_must_be_ComposedSequenceExpression(cls, v: str) -> str:
        if v == 'ComposedSequenceExpression':
            pass
        else:
            raise ValueError('type can only contain the word ComposedSequenceExpression')
        return v.title()
    @field_validator('components')
    @classmethod
    def check_components(cls, v: list) -> list:
        for component in v:
            fits_in_class=False
            try:
                DerivedSequenceExpression(**component)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    LiteralSequenceExpression(**component)
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    RepeatedSequenceExpression(**component)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('components must be an array containing any format possible between DerivedSequenceExpression, LiteralSequenceExpression or RepeatedSequenceExpression. It is mandatory to at least be one of DerivedSequenceExpression or RepeatedSequenceExpression')

class Allele(BaseModel, extra='forbid'):
    id: Optional[str] = Field(default=None, alias='_id')
    type: str
    location: Union[str,ChromosomeLocation,SequenceLocation]
    state: Union[ComposedSequenceExpression, DerivedSequenceExpression, LiteralSequenceExpression, RepeatedSequenceExpression]
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_Allele(cls, v: str) -> str:
        if v == 'Allele':
            pass
        else:
            raise ValueError('type can only contain the word Allele')
        return v.title()
    @field_validator('location')
    @classmethod
    def location_must_be_CURIE(cls, v: str) -> str:
        if isinstance(v, str):
            if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
                pass
            else:
                raise ValueError('location, if string, must be CURIE, e.g. NCIT:C42331')
            return v.title()
        
class Haplotype(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    members: list
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_Haplotype(cls, v: str) -> str:
        if v == 'Haplotype':
            pass
        else:
            raise ValueError('type can only contain the word Haplotype')
        return v.title()
    @field_validator('members')
    @classmethod
    def check_members(cls, v: list) -> list:
        for member in v:
            if isinstance(member, str):
                if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
                    pass
                else:
                    raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
            else:
                fits_in_class=False
                try:
                    Allele(**member)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
                if fits_in_class == False:
                    raise ValueError('members must be an array of items that fit CURIE or Allele')
        return v.title()

class Gene(BaseModel, extra='forbid'):
    type: str
    gene_id: str
    @field_validator('type')
    @classmethod
    def type_must_be_Gene(cls, v: str) -> str:
        if v == 'Gene':
            pass
        else:
            raise ValueError('type can only contain the word Gene')
        return v.title()
    @field_validator('gene_id')
    @classmethod
    def gene_id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class CopyNumberChange(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    subject: Union[str, ChromosomeLocation, Gene, SequenceLocation]
    copy_change: str
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_CopyNumberChange(cls, v: str) -> str:
        if v == 'CopyNumberChange':
            pass
        else:
            raise ValueError('type can only contain the word CopyNumberChange')
        return v.title()
    @field_validator('copy_change')
    @classmethod
    def check_copy_change(cls, v: str) -> str:
        if v in ["efo:0030069","efo:0020073","efo:0030068","efo:0030067","efo:0030064","efo:0030070","efo:0030071","efo:0030072"]:
            pass
        else:
            raise ValueError('copy_change "MUST be one of \"efo:0030069\" (complete genomic loss), \"efo:0020073\" (high-level loss),  \"efo:0030068\" (low-level loss), \"efo:0030067\" (loss), \"efo:0030064\" (regional base ploidy),  \"efo:0030070\" (gain), \"efo:0030071\" (low-level gain), \"efo:0030072\" (high-level gain).')
        return v.title()
    
class CopyNumberCount(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    subject: Union[str, ChromosomeLocation, Gene, SequenceLocation]
    copies: Union[DefiniteRange, IndefiniteRange, Number]
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_CopyNumberCount(cls, v: str) -> str:
        if v == 'CopyNumberCount':
            pass
        else:
            raise ValueError('type can only contain the word CopyNumberCount')
        return v.title()
    
class GenotypeMember(BaseModel, extra='forbid'):
    type: str
    count: Union[DefiniteRange, IndefiniteRange, Number]
    variation: Union[Allele, Haplotype]
    @field_validator('type')
    @classmethod
    def type_must_be_GenotypeMember(cls, v: str) -> str:
        if v == 'GenotypeMember':
            pass
        else:
            raise ValueError('type can only contain the word GenotypeMember')
        return v.title()
    
class Genotype(BaseModel, extra='forbid'):
    id: Optional[str]=Field(default=None, alias='_id')
    type: str
    members: list
    count: Union[DefiniteRange, IndefiniteRange, Number]
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('type')
    @classmethod
    def type_must_be_Genotype(cls, v: str) -> str:
        if v == 'Genotype':
            pass
        else:
            raise ValueError('type can only contain the word Genotype')
        return v.title()
    @field_validator('members')
    @classmethod
    def check_exposures(cls, v: list) -> list:
        for member in v:
            GenotypeMember(**member)

class LegacyVariation(BaseModel, extra='forbid'):
    alternateBases: str
    location: Union[str,ChromosomeLocation,SequenceLocation]
    referenceBases: Optional[str] = None
    variantType: str
    @field_validator('alternateBases')
    @classmethod
    def check_alternateBases(cls, v: str) -> str:
        if re.match("^([ACGTUNRYSWKMBDHV\\-\\.]*)$", v):
            pass
        else:
            raise ValueError('alternateBases must be a valid base from ACGTUNRYSWKMBDHV')
        return v.title()
    @field_validator('referenceBases')
    @classmethod
    def check_referenceBases(cls, v: str) -> str:
        if re.match("^([ACGTUNRYSWKMBDHV\\-\\.]*)$", v):
            pass
        else:
            raise ValueError('referenceBases must be a valid base from ACGTUNRYSWKMBDHV')
        return v.title()
    
class SoftwareTool(BaseModel, extra='forbid'):
    toolName: str
    toolReferences: dict
    version: str
    
class PhenoClinicEffect(BaseModel, extra='forbid'):
    annotatedWith: Optional[SoftwareTool]=None
    category: Optional[OntologyTerm]=None
    clinicalRelevance: Optional[str] = None
    conditionId: str
    effect: OntologyTerm
    evidenceType: Optional[OntologyTerm]=None
    @field_validator('clinicalRelevance')
    @classmethod
    def check_clinicalRelevance(cls, v: str) -> str:
        if v in ["benign","likely benign","uncertain significance","likely pathogenic","pathogenic"]:
            pass
        else:
            raise ValueError('clinicalRelevance must be a valid string from ["benign","likely benign","uncertain significance","likely pathogenic","pathogenic"]')
        return v.title()    
    
class CaseLevelVariant(BaseModel, extra='forbid'):
    alleleOrigin: Optional[OntologyTerm] =None
    analysisId: Optional[str]=None
    biosampleId: str
    clinicalInterpretations: Optional[list]=None
    id: Optional[str]=None
    individualId: Optional[str]=None
    phenotypicEffects: Optional[list]=None
    runId: Optional[str]=None
    zygosity: Optional[OntologyTerm] =None
    @field_validator('clinicalInterpretations')
    @classmethod
    def check_clinicalInterpretations(cls, v: list) -> list:
        for interpretation in v:
            PhenoClinicEffect(**interpretation)
    @field_validator('phenotypicEffects')
    @classmethod
    def check_phenotypicEffects(cls, v: list) -> list:
        for phenotypicEffect in v:
            PhenoClinicEffect(**phenotypicEffect)

class PopulationFrequency(BaseModel, extra='forbid'):
    alleleFrequency: Union[float, int]
    population: str

class FrequencyInPopulation(BaseModel, extra='forbid'):
    frequencies: list
    source: str
    sourceReference: str
    version: Optional[str]=None
    @field_validator('frequencies')
    @classmethod
    def check_frequencies(cls, v: list) -> list:
        for frequency in v:
            PopulationFrequency(**frequency)

class Identifiers(BaseModel, extra='forbid'):
    clinvarVariantId: Optional[str]=None
    genomicHGVSId: Optional[str]=None
    proteinHGVSIds: Optional[list]=None
    transcriptHGVSIds: Optional[list]=None
    variantAlternativeIds: Optional[list]=None
    @field_validator('clinvarVariantId')
    @classmethod
    def check_clinvarVariantId(cls, v: str) -> str:
        if re.match("^(clinvar:)?\\d+$", v):
            pass
        else:
            raise ValueError('clinvarVariantId must be a valid clinvar string')
        return v.title()
    @field_validator('proteinHGVSIds')
    @classmethod
    def check_proteinHGVSIds(cls, v: list) -> list:
        for proteinHGVSId in v:
            if isinstance(proteinHGVSId, str):
                pass
            else:
                raise ValueError('proteinHGVSIds must be an array of strings')
        return v.title()
    @field_validator('transcriptHGVSIds')
    @classmethod
    def check_transcriptHGVSIds(cls, v: list) -> list:
        for transcriptHGVSId in v:
            if isinstance(transcriptHGVSId, str):
                pass
            else:
                raise ValueError('transcriptHGVSIds must be an array of strings')
        return v.title()
    @field_validator('variantAlternativeIds')
    @classmethod
    def check_variantAlternativeIds(cls, v: list) -> list:
        for alternative in v:
            Reference(**alternative)

class GenomicFeature(BaseModel, extra='forbid'):
    featureClass: OntologyTerm
    featureId: Optional[OntologyTerm]=None

class MolecularAttributes(BaseModel, extra='forbid'):
    aminoacidChanges: Optional[list]=None
    geneIds: Optional[list]=None
    genomicFeatures: Optional[list]=None
    molecularEffects: Optional[list]=None
    @field_validator('aminoacidChanges')
    @classmethod
    def check_aminoacidChanges(cls, v: list) -> list:
        for aminoacidChange in v:
            if isinstance(aminoacidChange, str):
                pass
            else:
                raise ValueError('aminoacidChanges must be an array of strings')
        return aminoacidChange.title()
    @field_validator('geneIds')
    @classmethod
    def check_geneIds(cls, v: list) -> list:
        for geneId in v:
            if isinstance(geneId, str):
                pass
            else:
                raise ValueError('geneIds must be an array of strings')
        return geneId.title()
    @field_validator('genomicFeatures')
    @classmethod
    def check_genomicFeatures(cls, v: list) -> list:
        for genomicFeature in v:
            GenomicFeature(**genomicFeature)
    @field_validator('molecularEffects')
    @classmethod
    def check_molecularEffects(cls, v: list) -> list:
        for molecularEffect in v:
            OntologyTerm(**molecularEffect)

class VariantLevelData(BaseModel, extra='forbid'):
    clinicalInterpretations: Optional[list]=None
    phenotypicEffects: Optional[list]=None
    @field_validator('clinicalInterpretations')
    @classmethod
    def check_clinicalInterpretations(cls, v: list) -> list:
        for interpretation in v:
            PhenoClinicEffect(**interpretation)
    @field_validator('phenotypicEffects')
    @classmethod
    def check_phenotypicEffects(cls, v: list) -> list:
        for phenotypicEffect in v:
            PhenoClinicEffect(**phenotypicEffect)

class GenomicVariations(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass
        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    caseLevelData: Optional[list] = None
    frequencyInPopulations: Optional[list] = None
    identifiers: Optional[Identifiers] = None
    molecularAttributes: Optional[MolecularAttributes] = None
    variantInternalId: str
    variantLevelData: Optional[VariantLevelData]=None
    variation: Union[LegacyVariation, Allele, Haplotype, CopyNumberChange, CopyNumberCount, Genotype]
    @field_validator('caseLevelData')
    @classmethod
    def check_caseLevelData(cls, v: list) -> list:
        for case in v:
            CaseLevelVariant(**case)
    @field_validator('frequencyInPopulations')
    @classmethod
    def check_frequencyInPopulations(cls, v: list) -> list:
        for fp in v:
            FrequencyInPopulation(**fp)