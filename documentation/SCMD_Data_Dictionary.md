# SCMD Data Dictionary

**Source file:** scmd_provisional_202605.csv (Provisional SCMD with indicative price, May 2026)
**Rows:** 312,457 data rows (+1 header)
**Retrieved:** 11 Aug 2026 from NHSBSA Open Data Portal

## Columns

### YEAR_MONTH
- Type: integer, format YYYYMM (not a real date)
- Description: the month this data covers
- Example values: 202605
- Nulls: none — every row has it
- Notes: always 202605 in this file; spec expected separate Period_Year + Period_Month

### ODS_CODE
- Type: text (string) — letters + digits, e.g. RA2
- Description: NHS Organisation Data Service code identifying the trust that issued the medicine
- Example values: RA2, RTH, RTR
- Nulls: none observed — every row has a code
- Notes: file gives only the code, not the trust's name; resolving names needs a separate ODS lookup (Week 2 enrichment). Read as text, not a number.

### VMP_SNOMED_CODE
- Type: text (string) — a long numeric identifier, but NOT a number to calculate with
- Description: dm+d SNOMED-CT code for the medicine (VMP level)
- Example values: 31142211000001108, 18411511000001103, 18671811000001106
- Nulls: none observed in sample (confirm in validation)
- Notes: Excel/naive parsers corrupt this into scientific notation and round off digits — must be read as string (dtype=str in pandas)

### VMP_PRODUCT_NAME
- Type: text (string)
- Description: the medicine name in dm+d format
- Example values: "Sacubitril 97mg / Valsartan 103mg tablets", "Sodium citrate 441.17mg/5ml oral solution"
- Nulls: none observed in sample (confirm in validation)
- Notes: contains commas, so must stay quoted when parsing CSV; one name per SNOMED code

### UNIT_OF_MEASURE_IDENTIFIER
- Type: text (string) — a numeric code, treated as an identifier
- Description: SNOMED code for the unit the quantity is measured in
- Example values: 428673006 (TABLET), 258773002 (ML), 419702001 (PATCH)
- Nulls: none observed in sample (confirm in validation)
- Notes: pairs 1:1 with UNIT_OF_MEASURE_NAME; not in the original spec

### UNIT_OF_MEASURE_NAME
- Type: text (string)
- Description: human-readable unit for the quantity
- Example values: TABLET, ML, PATCH, CAPSULE, LITRE, KIT
- Nulls: none observed in sample (confirm in validation)
- Notes: because units differ per medicine, quantities are NOT additive across rows

### TOTAL_QUANITY_IN_VMP_UNIT
- Type: number (float)
- Description: total quantity of the medicine issued that month, in its VMP unit
- Example values: 280, 300, 1800, 56
- Nulls: (confirm in validation)
- Notes: header is MISSPELLED "QUANITY" — must be typed exactly in code; values ship as quoted strings with trailing dots ("280."); only sum within a single unit

### INDICATIVE_COST
- Type: number (float), GBP
- Description: estimated cost of the medicine issued (not actual net spend)
- Example values: 457.8, 47, 282, 34822.67
- Nulls: (confirm in validation — likely some where no price mapping exists)
- Notes: indicative only, overstates true spend (excludes confidential rebates); range is very wide, roughly £12 to £34,000+ per row

## Sample Rows

​```
YEAR_MONTH,"ODS_CODE",VMP_SNOMED_CODE,"VMP_PRODUCT_NAME",UNIT_OF_MEASURE_IDENTIFIER,"UNIT_OF_MEASURE_NAME",TOTAL_QUANITY_IN_VMP_UNIT,INDICATIVE_COST
202605,"RA2",31142211000001108,"Sacubitril 97mg / Valsartan 103mg tablets",428673006,"TABLET","280.","457.8"
202605,"RA2",18411511000001103,"Sodium citrate 441.17mg/5ml oral solution",258773002,"ML","300.","47."
202605,"RTH",18411511000001103,"Sodium citrate 441.17mg/5ml oral solution",258773002,"ML","1800.","282."
202605,"RA2",18671811000001106,"Tapentadol 100mg modified-release tablets",428673006,"TABLET","56.","25.03"
​```

## Data Quality Observations
1. Header typo: TOTAL_QUANITY_IN_VMP_UNIT is misspelled — must be typed exactly in code.
2. No trust name in the file — only ODS_CODE; needs an external ODS lookup for readable names.
3. Mixed units (TABLET, ML, PATCH...) mean TOTAL_QUANITY values aren't additive across medicines.
4. SNOMED codes get corrupted by Excel into scientific notation — must be read as text.
5. INDICATIVE_COST spans a huge range (~£12 to £34,000+); outliers need checking in validation.