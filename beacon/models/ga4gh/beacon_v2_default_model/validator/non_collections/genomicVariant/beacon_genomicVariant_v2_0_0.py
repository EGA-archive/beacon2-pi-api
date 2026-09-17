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
from beacon.framework.validator.v2_0_0.common import OntologyTerm

import re
from typing import Optional, Union, List
from pydantic import BaseModel, Field, field_validator


# ============================================================
# REGEX HELPERS
# ============================================================

# CURIE pattern used across multiple models.
# Example valid CURIE: NCIT:C42331
# Format: <namespace>:<identifier>
CURIE_REGEX = re.compile(r"^[A-Za-z0-9]+:[A-Za-z0-9]+$")

# Cytoband format validation used for chromosome intervals.
# This follows ISCN-style notation such as p11, qter, cen, etc.
CYTOBAND_REGEX = re.compile(r"^cen|[pq](ter|([1-9][0-9]*(\.[1-9][0-9]*)?))$")


def validate_curie(v: str, field: str) -> str:
    """
    Shared CURIE validation logic used across multiple models.

    This avoids repeating the same regex check in every field validator.
    """
    if not CURIE_REGEX.match(v):
        raise ValueError(f"{field} must be CURIE, e.g. NCIT:C42331")
    return v


# ============================================================
# BASIC DOMAIN MODELS
# ============================================================

class Members(BaseModel):
    """
    Represents a member entity in a group or dataset context.
    """
    affected: bool
    memberId: str
    role: "OntologyTerm"  # external ontology-based role definition


class Reference(BaseModel):
    """
    Generic reference object that may point to external literature or metadata.
    """
    id: Optional[str] = None
    notes: Optional[str] = None
    reference: Optional[str] = None


# ============================================================
# NUMERIC REPRESENTATIONS
# ============================================================

class Number(BaseModel):
    """
    Represents a single numeric value with strict type tagging.
    """
    type: str
    value: int

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Ensures schema discrimination consistency
        if v != "Number":
            raise ValueError("type can only contain the word Number")
        return v


class DefiniteRange(BaseModel):
    """
    Represents a closed numeric interval [min, max].
    """
    type: str
    min: Union[int, float]
    max: Union[int, float]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Strict type tag ensures correct model resolution
        if v != "DefiniteRange":
            raise ValueError("type can only contain the word DefiniteRange")
        return v


class IndefiniteRange(BaseModel):
    """
    Represents an open-ended numeric range using a comparator.
    """
    type: str
    value: Union[int, float]
    comparator: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Enforces correct discriminated union behavior
        if v != "IndefiniteRange":
            raise ValueError("type can only contain the word IndefiniteRange")
        return v

    @field_validator("comparator")
    @classmethod
    def validate_comparator(cls, v: str) -> str:
        # Only two valid directional comparisons are supported
        if v not in ("<=", ">="):
            raise ValueError("comparator must be <= or >=")
        return v


# ============================================================
# INTERVAL MODELS
# ============================================================

class CytobandInterval(BaseModel):
    """
    Represents a cytogenetic band interval (ISCN notation).
    """
    type: str
    start: str
    end: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Ensures correct interval subtype
        if v != "CytobandInterval":
            raise ValueError("type can only contain the word CytobandInterval")
        return v

    @field_validator("start", "end")
    @classmethod
    def validate_cytoband(cls, v: str) -> str:
        # Validates ISCN cytoband formatting rules
        if not CYTOBAND_REGEX.match(v):
            raise ValueError(
                "must be valid ISCN cytoband notation"
            )
        return v


class SimpleInterval(BaseModel):
    """
    Represents a simple integer-based genomic interval.
    """
    type: str
    start: int
    end: int

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "SimpleInterval":
            raise ValueError("type can only contain the word SimpleInterval")
        return v


class SequenceInterval(BaseModel):
    """
    Represents a flexible interval that may use numeric or range types.
    """
    type: str
    start: Union[DefiniteRange, IndefiniteRange, Number]
    end: Union[DefiniteRange, IndefiniteRange, Number]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "SequenceInterval":
            raise ValueError("type can only contain the word SequenceInterval")
        return v


# ============================================================
# LOCATION MODELS
# ============================================================

class ChromosomeLocation(BaseModel):
    """
    Represents a genomic location on a chromosome with cytoband resolution.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    type: str
    species_id: str
    chr: str
    interval: CytobandInterval

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        # Ensures external identifier follows CURIE format
        return validate_curie(v, "_id")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "ChromosomeLocation":
            raise ValueError("type can only contain the word ChromosomeLocation")
        return v

    @field_validator("species_id")
    @classmethod
    def validate_species(cls, v: str) -> str:
        # Species must also follow CURIE format
        return validate_curie(v, "species_id")

    @field_validator("chr")
    @classmethod
    def validate_chr(cls, v: str) -> str:
        # Only human chromosomes are allowed in this schema
        allowed = {str(i) for i in range(1, 23)} | {"X", "Y"}
        if v not in allowed:
            raise ValueError("chr must be 1-22, X, or Y")
        return v


class SequenceLocation(BaseModel):
    """
    Represents a location on a biological sequence (not necessarily chromosomal).
    """
    id: Optional[str] = Field(default=None, alias="_id")
    type: str
    sequence_id: str
    interval: Union[SequenceInterval, SimpleInterval]

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        # External identifier must follow CURIE standard
        return validate_curie(v, "_id")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "SequenceLocation":
            raise ValueError("type can only contain the word SequenceLocation")
        return v

    #@field_validator("sequence_id")
    #@classmethod
    #def validate_sequence_id(cls, v: str) -> str:
        #return validate_curie(v, "sequence_id")


# ============================================================
# SEQUENCE EXPRESSION MODELS
# ============================================================

class DerivedSequenceExpression(BaseModel):
    """
    Sequence derived from a location, optionally reverse complemented.
    """
    type: str
    location: SequenceLocation
    reverse_complement: bool

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "DerivedSequenceExpression":
            raise ValueError("type can only contain the word DerivedSequenceExpression")
        return v


class LiteralSequenceExpression(BaseModel):
    """
    Raw biological sequence expressed explicitly as a string.
    """
    type: str
    sequence: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "LiteralSequenceExpression":
            raise ValueError("type can only contain the word LiteralSequenceExpression")
        return v

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: str) -> str:
        # Restrict to amino acid / nucleotide-like alphabet with ambiguity codes
        if not re.match(r"^[A-Z*\-]*$", v):
            raise ValueError(
                "sequence must be a valid biological sequence (IUPAC allowed)"
            )
        return v
import re
from typing import Union, Optional, List
from pydantic import BaseModel, Field, field_validator


# ============================================================
# SEQUENCE EXPRESSION COMBINATORS
# ============================================================

class RepeatedSequenceExpression(BaseModel):
    """
    Represents a sequence expression that is repeated N times.
    Used for tandem repeats or duplicated sequence structures.
    """

    type: str

    # seq_expr can be either a derived (computed from location)
    # or literal (explicit sequence string)
    seq_expr: Union[
        "DerivedSequenceExpression",
        "LiteralSequenceExpression"
    ]

    # repetition count can be fixed or ranged
    count: Union["DefiniteRange", "IndefiniteRange", "Number"]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Ensures correct discriminated union routing
        if v != "RepeatedSequenceExpression":
            raise ValueError("type can only contain the word RepeatedSequenceExpression")
        return v


class ComposedSequenceExpression(BaseModel):
    """
    Represents a composite sequence made of multiple components.
    Components may be mixed sequence expression types.
    """

    # Optional but expected discriminator field
    type: Optional[str] = None

    # Raw heterogeneous list of sequence components
    components: list

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Ensures model identity consistency
        if v != "ComposedSequenceExpression":
            raise ValueError("type can only contain the word ComposedSequenceExpression")
        return v

    @field_validator("components")
    @classmethod
    def validate_components(cls, v: list) -> list:
        """
        Each component must match at least one allowed sequence model:
        - DerivedSequenceExpression
        - LiteralSequenceExpression
        - RepeatedSequenceExpression
        """

        for component in v:

            # Try validating against each allowed model type
            for model in (
                "DerivedSequenceExpression",
                "LiteralSequenceExpression",
                "RepeatedSequenceExpression",
            ):
                try:
                    # dynamic validation attempt
                    globals()[model](**component)
                    break
                except Exception:
                    continue

            # If none matched, reject component
            else:
                raise ValueError(
                    "components must contain valid sequence expressions "
                    "(Derived, Literal, or Repeated)"
                )

        return v


# ============================================================
# CORE VARIANT MODEL
# ============================================================

class Allele(BaseModel):
    """
    Represents an allele with location and structural state.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    type: str

    # location can be:
    # - CURIE string
    # - ChromosomeLocation object
    # - SequenceLocation object
    location: Union[str, "ChromosomeLocation", "SequenceLocation"]

    # structural representation of the allele
    state: Union[
        ComposedSequenceExpression,
        "DerivedSequenceExpression",
        "LiteralSequenceExpression",
        RepeatedSequenceExpression,
    ]

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        # CURIE validation for external identifiers
        if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("_id must be CURIE, e.g. NCIT:C42331")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Ensures strict model discrimination
        if v != "Allele":
            raise ValueError("type can only contain the word Allele")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        # Only validate string-based location formats
        if isinstance(v, str):
            if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
                raise ValueError(
                    "location string must be CURIE, e.g. NCIT:C42331"
                )
        return v


# ============================================================
# HAPLOTYPE MODEL
# ============================================================

class Haplotype(BaseModel):
    """
    A haplotype is a collection of allele members.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    type: str
    members: list

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("_id must be CURIE, e.g. NCIT:C42331")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "Haplotype":
            raise ValueError("type can only contain the word Haplotype")
        return v

    @field_validator("members")
    @classmethod
    def validate_members(cls, v: list) -> list:
        """
        Members must be CURIE strings if provided as strings.
        """
        for member in v:
            if isinstance(member, str):
                if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", member):
                    raise ValueError("member must be CURIE, e.g. NCIT:C42331")
        return v


# ============================================================
# GENE MODEL
# ============================================================

class Gene(BaseModel):
    """
    Gene entity represented by a CURIE identifier.
    """

    type: str
    gene_id: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "Gene":
            raise ValueError("type can only contain the word Gene")
        return v

    @field_validator("gene_id")
    @classmethod
    def validate_gene_id(cls, v: str) -> str:
        if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("gene_id must be CURIE, e.g. NCIT:C42331")
        return v


# ============================================================
# COPY NUMBER VARIATION MODELS
# ============================================================

class CopyNumberChange(BaseModel):
    """
    Represents qualitative copy number change events.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    type: str
    subject: Union[str, "ChromosomeLocation", Gene, "SequenceLocation"]
    copy_change: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("_id must be CURIE, e.g. NCIT:C42331")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "CopyNumberChange":
            raise ValueError("type can only contain the word CopyNumberChange")
        return v

    @field_validator("copy_change")
    @classmethod
    def validate_copy_change(cls, v: str) -> str:
        # Controlled vocabulary (EFO ontology terms)
        allowed = {
            "efo:0030069",
            "efo:0020073",
            "efo:0030068",
            "efo:0030067",
            "efo:0030064",
            "efo:0030070",
            "efo:0030071",
            "efo:0030072",
        }

        if v not in allowed:
            raise ValueError(
                "copy_change must be a valid EFO copy number term"
            )
        return v


class CopyNumberCount(BaseModel):
    """
    Represents numeric copy number estimation.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    type: str
    subject: Union[str, "ChromosomeLocation", Gene, "SequenceLocation"]
    copies: Union["DefiniteRange", "IndefiniteRange", "Number"]

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("_id must be CURIE, e.g. NCIT:C42331")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "CopyNumberCount":
            raise ValueError("type can only contain the word CopyNumberCount")
        return v


# ============================================================
# GENOTYPE MODEL
# ============================================================

class GenotypeMember(BaseModel):
    """
    Represents a genotype component combining variation + count.
    """

    type: str
    count: Union["DefiniteRange", "IndefiniteRange", "Number"]
    variation: Union["Allele", Haplotype]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v != "GenotypeMember":
            raise ValueError("type can only contain the word GenotypeMember")
        return v
    
class Genotype(BaseModel):
    # Unique identifier for the genotype (optional CURIE-formatted ID)
    id: Optional[str] = Field(default=None, alias='_id')

    # Fixed entity type discriminator (must always be "Genotype")
    type: str

    # List of genotype member objects (validated via GenotypeMember)
    members: list

    # Copy/state count representation (can be range or numeric form)
    count: Union[DefiniteRange, IndefiniteRange, Number]

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensure ID follows CURIE format (prefix:value)
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('_id must be CURIE, e.g. NCIT:C42331')
        return v

    @field_validator('type')
    @classmethod
    def type_must_be_Genotype(cls, v: str) -> str:
        # Enforce strict type discrimination for schema safety
        if v == 'Genotype':
            pass
        else:
            raise ValueError('type can only contain the word Genotype')
        return v

    @field_validator('members')
    @classmethod
    def check_exposures(cls, v: list) -> list:
        # Validate each member conforms to GenotypeMember schema
        for member in v:
            GenotypeMember(**member)
        return v


class LegacyVariation(BaseModel):
    # Legacy variant representation using simple string-based fields
    alternateBases: str
    location: Union[str, ChromosomeLocation, SequenceLocation]
    referenceBases: Optional[str] = None
    variantType: str

    @field_validator('alternateBases')
    @classmethod
    def check_alternateBases(cls, v: str) -> str:
        # Validate allowed nucleotide ambiguity codes for alternate bases
        if re.match("^([ACGTUNRYSWKMBDHV\\-\\.]*)$", v):
            pass
        else:
            raise ValueError('alternateBases must be a valid base from ACGTUNRYSWKMBDHV')
        return v

    @field_validator('referenceBases')
    @classmethod
    def check_referenceBases(cls, v: str) -> str:
        # Same validation rules as alternateBases (IUPAC-compatible alphabet)
        if re.match("^([ACGTUNRYSWKMBDHV\\-\\.]*)$", v):
            pass
        else:
            raise ValueError('referenceBases must be a valid base from ACGTUNRYSWKMBDHV')
        return v


class SoftwareTool(BaseModel):
    # Tool metadata used for annotation provenance
    toolName: str
    toolReferences: dict  # external identifiers / citations
    version: str


class PhenoClinicEffect(BaseModel):
    # Optional annotation tool used to generate clinical interpretation
    annotatedWith: Optional[SoftwareTool] = None

    # Ontology-based categorization of phenotype effect
    category: Optional[OntologyTerm] = None

    # Clinical interpretation category (e.g. pathogenicity)
    clinicalRelevance: Optional[str] = None

    # Required disease/condition identifier
    conditionId: str

    # Ontology-based clinical effect descriptor
    effect: OntologyTerm

    # Optional evidence classification (ontology-driven)
    evidenceType: Optional[OntologyTerm] = None

    @field_validator('clinicalRelevance')
    @classmethod
    def check_clinicalRelevance(cls, v: str) -> str:
        # Restrict clinical interpretation to ACMG-like categories
        if v in ["benign", "likely benign", "uncertain significance", "likely pathogenic", "pathogenic"]:
            pass
        else:
            raise ValueError(
                'clinicalRelevance must be a valid string from '
                '["benign","likely benign","uncertain significance","likely pathogenic","pathogenic"]'
            )
        return v


class CaseLevelVariant(BaseModel):
    # Optional biological context fields linking variant to sample/analysis
    alleleOrigin: Optional[OntologyTerm] = None
    analysisId: Optional[str] = None
    biosampleId: str

    # Clinical interpretation list (validated as PhenoClinicEffect objects)
    clinicalInterpretations: Optional[list] = None

    id: Optional[str] = None
    individualId: Optional[str] = None

    # Phenotypic consequences at case level
    phenotypicEffects: Optional[list] = None

    runId: Optional[str] = None
    zygosity: Optional[OntologyTerm] = None

    @field_validator('clinicalInterpretations')
    @classmethod
    def check_clinicalInterpretations(cls, v: list) -> list:
        # Ensure each interpretation conforms to structured phenotype schema
        for interpretation in v:
            PhenoClinicEffect(**interpretation)
        return v

    @field_validator('phenotypicEffects')
    @classmethod
    def check_phenotypicEffects(cls, v: list) -> list:
        # Validate phenotypic effects using same interpretation model
        for phenotypicEffect in v:
            PhenoClinicEffect(**phenotypicEffect)
        return v


class PopulationFrequency(BaseModel):
    # Frequency value (can be float or integer depending on representation)
    alleleFrequency: Union[float, int]
    population: str


class FrequencyInPopulation(BaseModel):
    # List of population frequency entries
    frequencies: list
    source: str
    sourceReference: str
    version: Optional[str] = None

    @field_validator('frequencies')
    @classmethod
    def check_frequencies(cls, v: list) -> list:
        # Validate nested population frequency objects
        for frequency in v:
            PopulationFrequency(**frequency)
        return v


class Identifiers(BaseModel):
    # Variant identifier fields across multiple external systems
    clinvarVariantId: Optional[str] = None
    genomicHGVSId: Optional[str] = None
    proteinHGVSIds: Optional[list] = None
    transcriptHGVSIds: Optional[list] = None
    variantAlternativeIds: Optional[list] = None

    @field_validator('clinvarVariantId')
    @classmethod
    def check_clinvarVariantId(cls, v: str) -> str:
        # Accept numeric ClinVar IDs or prefixed form
        if re.match("^(clinvar:)?\\d+$", v):
            pass
        else:
            raise ValueError('clinvarVariantId must be a valid clinvar string')
        return v

    @field_validator('proteinHGVSIds')
    @classmethod
    def check_proteinHGVSIds(cls, v: list) -> list:
        # Ensure all protein HGVS IDs are strings
        for proteinHGVSId in v:
            if isinstance(proteinHGVSId, str):
                pass
            else:
                raise ValueError('proteinHGVSIds must be an array of strings')
        return v

    @field_validator('transcriptHGVSIds')
    @classmethod
    def check_transcriptHGVSIds(cls, v: list) -> list:
        # Ensure all transcript HGVS IDs are strings
        for transcriptHGVSId in v:
            if isinstance(transcriptHGVSId, str):
                pass
            else:
                raise ValueError('transcriptHGVSIds must be an array of strings')
        return v

    @field_validator('variantAlternativeIds')
    @classmethod
    def check_variantAlternativeIds(cls, v: list) -> list:
        # Validate structured reference objects for alternative identifiers
        for alternative in v:
            Reference(**alternative)
        return v


class GenomicFeature(BaseModel):
    # Feature classification and optional feature identifier
    featureClass: OntologyTerm
    featureId: Optional[OntologyTerm] = None


class MolecularAttributes(BaseModel):
    # Molecular-level annotation fields for variant interpretation
    aminoacidChanges: Optional[list] = None
    geneIds: Optional[list] = None
    genomicFeatures: Optional[list] = None
    molecularEffects: Optional[list] = None

    @field_validator('aminoacidChanges')
    @classmethod
    def check_aminoacidChanges(cls, v: list) -> list:
        # Ensure amino acid changes are simple strings
        for aminoacidChange in v:
            if isinstance(aminoacidChange, str):
                pass
            else:
                raise ValueError('aminoacidChanges must be an array of strings')
        return v

    @field_validator('geneIds')
    @classmethod
    def check_geneIds(cls, v: list) -> list:
        # Ensure gene IDs are string identifiers
        for geneId in v:
            if isinstance(geneId, str):
                pass
            else:
                raise ValueError('geneIds must be an array of strings')
        return v

    @field_validator('genomicFeatures')
    @classmethod
    def check_genomicFeatures(cls, v: list) -> list:
        # Validate nested genomic feature structures
        for genomicFeature in v:
            GenomicFeature(**genomicFeature)
        return v

    @field_validator('molecularEffects')
    @classmethod
    def check_molecularEffects(cls, v: list) -> list:
        # Ensure ontology-based molecular effect annotations
        for molecularEffect in v:
            OntologyTerm(**molecularEffect)
        return v

# This class will gather all the information about the variant level data and validate it
class VariantLevelData(BaseModel):
    clinicalInterpretations: Optional[list]=None
    phenotypicEffects: Optional[list]=None
    # This will validate clinicalInterpretations to be a list of PhenoClinicEffect objects
    @field_validator('clinicalInterpretations')
    @classmethod
    def check_clinicalInterpretations(cls, v: list) -> list:
        for interpretation in v:
            PhenoClinicEffect(**interpretation)
        return v
    # This will validate phenotypicEffects to be a list of PhenoClinicEffect objects
    @field_validator('phenotypicEffects')
    @classmethod
    def check_phenotypicEffects(cls, v: list) -> list:
        for phenotypicEffect in v:
            PhenoClinicEffect(**phenotypicEffect)
        return v

# This is the generic class to validate a record for genomic variants
class Genomicvariant(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass
        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    caseLevelData: Optional[list] = None
    frequencyInPopulations: Optional[list[FrequencyInPopulation]] = None
    identifiers: Optional[Identifiers] = None
    molecularAttributes: Optional[MolecularAttributes] = None
    variantInternalId: str
    variantLevelData: Optional[VariantLevelData]=None
    variation: Union[LegacyVariation, Allele, Haplotype, CopyNumberChange, CopyNumberCount, Genotype]
    # This will ensure caseLevelData is a list containing CaseLevelVariant objects class that is located in this same script
    @field_validator('caseLevelData')
    @classmethod
    def check_caseLevelData(cls, v: list) -> list:
        for case in v:
            CaseLevelVariant(**case)
        return v