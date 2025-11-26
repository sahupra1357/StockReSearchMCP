from sector.sec_parser import (
    extract_business_section,
    extract_risk_factors,
    extract_mda_section,
    extract_properties_section,
    extract_business_section_from_file
)

# with open("./output/sec_filings/sec-edgar-filings/NVDA/10-K/0001012870-02-002262/full-submission.txt", "r", encoding="utf-8") as f:
#     filing = f.read()

# business = extract_business_section(filing)
# risks = extract_risk_factors(filing)
# mda = extract_mda_section(filing)
# props = extract_properties_section(filing)

# #print(business[:500])
# print(business)
# print("----- RISKS -----")
# print(risks)
# print("----- MDA -----")
# print(mda)
# print("----- PROPERTIES -----")
# print(props)

result_output = extract_business_section_from_file("./output/sec_filings/sec-edgar-filings/NVDA/10-K/0001012870-02-002262/full-submission.txt")
print(result_output)