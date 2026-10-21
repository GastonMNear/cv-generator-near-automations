"""Map Near's 89 HubSpot industries to Hirebase (industry, sub_industry) pairs.
Included subindustries = every sub that appears in the mapping; everything else is excluded."""
import csv, json

RAW = json.load(open("hirebase_subindustries_raw.json"))
AG, AR, CO, CG, CS, DE, ED, EM, EN, FI, HC, LE, MF, MC, NP, RE, RT, RW, TE, TL, WF = (
    "Agriculture", "Arts", "Construction", "Consumer Goods", "Corporate Services", "Design",
    "Education", "Energy & Mining", "Entertainment", "Finance", "Healthcare", "Legal",
    "Manufacturing", "Media & Communications", "Nonprofit", "Real Estate", "Recreation & Travel",
    "Retail & Wholesale", "Tech, Software & IT Services", "Transportation & Logistics",
    "Wellness & Fitness")

def allof(ind, conf, note="", exclude=()):
    return [(ind, s, conf, note) for s in RAW[ind] if s not in exclude]

# hubspot_industry -> [(hirebase_industry, sub_industry, confidence, note)]
M = {
"Computer Software": [(TE,"Software Development & Engineering","high",""),(TE,"Enterprise Software & Solutions","high",""),
    (TE,"Cloud Technologies","high",""),(TE,"AI & ML","high",""),(TE,"Data Management & Analytics","med",""),
    (TE,"Emerging Technologies","med",""),(TE,"Legal & Compliance Technology","med","vertical SaaS"),
    (TE,"Health Information Technology","med","vertical SaaS"),(TE,"Educational Technology (EdTech)","med","vertical SaaS"),
    (TE,"Retail & Point of Sale Technology","med","vertical SaaS"),(TE,"Energy & Utilities Technology","med","vertical SaaS"),
    (TE,"Real Estate Technology","med","proptech; same string also under Real Estate"),(TE,"Web3/Crypto","med",""),
    (CO,"Construction Technology & Automation","med","contech"),(HC,"Healthcare Technology","med",""),
    (FI,"Fintech","med",""),(RT,"Travel Technology","med",""),(AG,"Agri-Tech & Digital Agriculture","med",""),
    (WF,"Wellness Apps & Digital Platforms","med","")],
"Marketing and Advertising": [(CS,"Marketing & Advertising","high",""),(MC,"Advertising & Marketing","high",""),
    (RE,"Real Estate Marketing & Advertising","med","")],
"Information Technology and Services": [(TE,"IT Services","high",""),(TE,"Cloud Technologies","med",""),
    (TE,"Data Management & Analytics","med",""),(TE,"Internet of Things (IoT)","med","")],
"Management Consulting": [(CS,"Management Consulting","high",""),(HC,"Healthcare Consulting & Management","med",""),
    (RE,"Real Estate Consulting","med",""),(TL,"Transportation Consulting & Services","med",""),
    (WF,"Health & Wellness Consulting","low",""),(RT,"Travel R&C","low","'R&C' undefined in docs; assumed research & consulting")],
"Financial Services": [(FI,"Credit & Lending","high","lenders, not banks (Banking excluded)"),(FI,"Payment Systems & Services","high",""),
    (FI,"Fintech","high",""),(FI,"Financial Planning & Advisory","high",""),(FI,"Finance Risk Management","med",""),
    (FI,"Leasing & Equipment Finance","med",""),(FI,"Real Estate Finance","med",""),(CS,"Financial Services for Corporates","high",""),
    (RE,"Real Estate Financing","med",""),(TE,"Web3/Crypto","low","")],
"Real Estate": allof(RE,"high",exclude={"Architecture & Design","Senior & Assisted Living Real Estate"})
    + [(CO,"Real Estate Development & Management","med",""),(CS,"Real Estate Services","high","")],
"Retail": [(RW,s,"high","") for s in ["Online Retail","Specialty Retail","Clothing & Apparel Stores","Electronics & Appliance Stores",
        "Furniture & Home Furnishings Stores","General Merchandise Stores","Health & Personal Care Stores","Sporting Goods, Hobby, Book & Music Stores"]]
    + [(MC,"Media Retail","med",""),(WF,"Sporting Goods & Retail","med","")],
"Accounting": [(CS,"Accounting","high",""),(FI,"Accounting & Auditing","high","")],
"Consumer Services": [(TE,"E-Commerce & Internet Services","low","no consumer-services bucket in Hirebase"),
    (CG,"Personal Care & Household","low","keyword: 'home services' / 'consumer services'")],
"Construction": allof(CO,"high"),
"Hospital & Health Care": [(HC,"Hospitals","high","")] + [(HC,s,"med","") for s in ["Medical Practices","Home Health Care","Ambulatory Care",
    "Rehabilitation","Medical & Diagnostic Labs","Healthcare Support Services","Telemedicine","Healthcare Consulting & Management","Medical Education & Training"]],
"Business Supplies and Equipment": [(CS,"Business Supplies & Equipment","high",""),(CG,"Stationery & Office Supplies","med","")],
"Consumer Goods": allof(CG,"high",exclude={"Wine & Spirits"}) + [(MF,"Consumer Goods Manufacturing","high",""),
    (MF,"Tobacco Manufacturing","low","consumer goods; include only for coverage")],
"Venture Capital & Private Equity": [(FI,"Investment","med","VC/PE sits inside Investment; keyword: 'venture capital' / 'private equity'"),
    (RE,"Real Estate Investing","low","")],
"Hospitality": [(RT,"Hospitality","high",""),(RE,"Vacation & Short-term Rentals","med","")],
"Apparel & Fashion": [(CG,"Apparel & Textiles","high",""),(MF,"Apparel Manufacturing","high",""),(DE,"Fashion Design","high",""),
    (RW,"Clothing & Apparel Stores","high",""),(AR,"Fashion & Textile Arts","med",""),(CG,"Luxury Goods","med",""),
    (DE,"Jewelry Design","med",""),(MF,"Jewelry & Silverware Manufacturing","med",""),(MF,"Leather & Allied Product Manufacturing","med",""),
    (EN,"Fashion & Lifestyle Entertainment","low","")],
"Capital Markets": [(FI,"Financial Markets","high",""),(FI,"Securities Brokerage & Trading","high","")],
"Health, Wellness and Fitness": allof(WF,"high") + [(HC,"Nutrition & Weight Loss","med",""),(RT,"Wellness & Spa","med",""),
    (CG,"Health & Wellness Products","med",""),(NP,"Health & Wellness Promotion","low","")],
"Insurance": [(FI,"Insurance","high",""),(HC,"Health Insurance","high",""),(RT,"Travel Insurance & Safety","med","")],
"Investment Management": [(FI,"Wealth Management","high",""),(FI,"Investment","high",""),(FI,"Pension Funds & Retirement Plans","med","")],
"Professional Training & Coaching": [(CS,"Professional Training & Coaching","high",""),(ED,"Corporate Training","high",""),
    (ED,"Professional Education","med",""),(ED,"Continuing Education","med","")],
"Food & Beverages": [(CG,"Food & Beverage","high","same string also under Recreation & Travel"),(RT,"Food & Beverage","high",""),
    (MF,"Food & Beverage Manufacturing","med","")],
"Facilities Services": [(CS,"Facilities Services","high",""),(RE,"Property Management","med","")],
"Transportation/Trucking/Railroad": [(TL,"Road Transportation","high",""),(TL,"Rail Transportation","high",""),
    (TL,"Specialized Transportation Services","med",""),(TL,"Intermodal & Multimodal Transportation","med",""),
    (TL,"Support Services & Infrastructure","med",""),(TL,"Postal Services","low","couriers/parcel"),
    (MF,"Railroad Rolling Stock Manufacturing","low",""),(RT,"Transportation for Travel","low","may include airlines (excluded industry)")],
"Legal Services": [(RE,"Real Estate Legal Services","high",""),(TE,"Legal & Compliance Technology","med","")]
    + allof(LE,"med","law-firm practice areas; also mapped under Law Practice"),
"Research": [(ED,"Research","high",""),(CS,"R&D Services","high",""),(HC,"Medical R&D","med",""),
    (NP,"Science & Technology Research","med",""),(NP,"Education and Research","med",""),(AG,"Agricultural R&D","low","")],
"Automotive": [(MF,"Automotive Manufacturing","high",""),(CG,"Automobiles & Auto Parts","high",""),(DE,"Automotive Design","med","")],
"Food Production": [(MF,"Food & Beverage Manufacturing","high",""),(AG,"Agro-Processing","med","")],
"E-Learning": [(ED,"E-Learning","high",""),(TE,"Educational Technology (EdTech)","high",""),(MC,"Media Education & Training","med",""),
    (WF,"Online Fitness & Wellness Courses","low","")],
"Electrical/Electronic Manufacturing": [(MF,"Electronics Manufacturing","high",""),
    (MF,"Electrical Equipment, Appliance & Component Manufacturing","high",""),(MF,"Computer & Peripheral Equipment Manufacturing","med","overlaps Computer Hardware (excluded) but also electronics")],
"Broadcast Media": [(MC,"Broadcasting","high",""),(EN,"Television","high",""),(EN,"Radio & Audio Entertainment","high",""),
    (NP,"Public Broadcasting & Media","med","")],
"Entertainment": [(EN,s,"high","") for s in ["Film & Movies","Television","Music","Video Games","Digital & Online Media",
        "Events & Live Entertainment","Animation","Radio & Audio Entertainment","VR & AR Entertainment"]]
    + [(EN,"Sports Entertainment","med",""),(EN,"Themed Entertainment","low","theme parks"),(EN,"Literary Entertainment","low","")]
    + [(MC,"Film & Entertainment","high",""),(MC,"Music Industry","high",""),(MC,"Gaming & Interactive Entertainment","high",""),
       (RT,"Attractions & Entertainment","med","")],
"Logistics and Supply Chain": [(TL,"Logistics & Supply Chain","high",""),(TL,"Intermodal & Multimodal Transportation","med",""),
    (TL,"Emerging Transportation Technologies","med",""),(TL,"Support Services & Infrastructure","med",""),
    (TL,"Transportation Consulting & Services","med","")],
"Investment Banking": [(FI,"Financial Markets","med","no IB bucket; keyword: 'investment banking' / 'M&A advisory'"),
    (FI,"Securities Brokerage & Trading","med",""),(FI,"Investment","med","")],
"Building Materials": [(CO,"Construction Materials & Equipment","high",""),(MF,"Nonmetallic Mineral Product Manufacturing","med",""),
    (MF,"Glass & Ceramic Manufacturing","med",""),(MF,"Wood Product Manufacturing","med","")],
"Pharmaceuticals": [(HC,"Pharmaceuticals","high",""),(WF,"Supplements & Nutraceuticals","med",""),(CG,"Health & Wellness Products","low","")],
"Cosmetics": [(CG,"Personal Care & Household","med","beauty mixed with household; keyword: 'cosmetics' / 'beauty' / 'skincare'"),
    (RW,"Health & Personal Care Stores","med","")],
"Education Management": [(ED,"Education Management","high",""),(ED,"Educational Support Services","med","")],
"Renewables & Environment": [(EM,"Renewable Energy","high",""),(EM,"Alternative Energy Sources","high",""),
    (CO,"Green & Sustainable Construction","med",""),(RE,"Sustainable Real Estate","med",""),(DE,"Sustainable/Green Design","low",""),
    (NP,"Environment & Wildlife","low","")],
"Wholesale": [(RW,"Wholesale","high",""),(AG,"Farm Supplies Wholesaling","med","")],
"Environmental Services": [(CS,"Environmental Services","high",""),(NP,"Environment & Wildlife","low","")],
"Machinery": [(MF,"Machinery Manufacturing","high",""),(MF,"Heavy Machinery Manufacturing","high",""),(AG,"Agricultural Machinery","med",""),
    (EM,"Mining Equipment & Technology","med",""),(MF,"Energy Equipment Manufacturing","med","")],
"Medical Devices": [(HC,"Medical Devices","high",""),(MF,"Medical Device Manufacturing","high","")],
"Mental Health Care": [(HC,"Mental Health Care","high",""),(WF,"Mental Wellness Programs","med","")],
"Media Production": [(EN,"Film & Movies","med",""),(MC,"Film & Entertainment","med",""),(MC,"Digital Media","med",""),
    (AR,"Digital & Multimedia Arts","med",""),(AR,"Cinematic Arts","med",""),(DE,"Motion Graphics Design","med",""),
    (AR,"Photography","low",""),(DE,"Sound Design","low","keyword: 'production company' / 'video production'")],
"Design": allof(DE,"high",exclude={"Architecture","Landscape Design"})
    + [(AR,"Architecture & Design","med","string also under Real Estate; kept for the Design side, not Architecture & Planning"),
       (RE,"Architecture & Design","med","same string as Arts")],
"Consumer Electronics": [(CG,"Consumer Electronics","high",""),(RW,"Electronics & Appliance Stores","med",""),
    (TE,"Hardware & Equipment","med","overlaps Computer Hardware (excluded)"),(MF,"Computer & Peripheral Equipment Manufacturing","med","")],
"Utilities": [(EM,"Electricity Generation & Distribution","high",""),(EM,"Nuclear Power","med",""),
    (TE,"Energy & Utilities Technology","med",""),(TL,"Pipeline Transportation","low","")],
"Mechanical or Industrial Engineering": [(CO,"Heavy & Civil Engineering","med",""),(DE,"Industrial Design","med",""),
    (MF,"Machinery Manufacturing","low",""),(EM,"Energy Equipment & Services","low","keyword: 'engineering services'")],
"Events Services": [(CS,"Events Services","high",""),(MC,"Events & Conferences","high",""),(EN,"Events & Live Entertainment","med",""),
    (AR,"Event & Festival Management","med",""),(DE,"Exhibition Design","low",""),(WF,"Fitness & Wellness Events & Expositions","low","")],
"Computer & Network Security": [(TE,"Cybersecurity","high","")],
"Telecommunications": [(MC,"Telecommunications","high",""),(TE,"Networking & Communications","med","")],
"Restaurants": [(RT,"Food & Beverage","med","no restaurant bucket; keyword: 'restaurant' / 'hospitality group'")],
"Internet": [(TE,"E-Commerce & Internet Services","high",""),(MC,"Digital Media","med",""),(EN,"Digital & Online Media","med",""),
    (RW,"Online Retail","med","")],
"Furniture": [(MF,"Furniture Manufacturing","high",""),(CG,"Home Furnishings & Improvement","high",""),
    (RW,"Furniture & Home Furnishings Stores","high",""),(DE,"Furniture Design","med",""),(DE,"Interior Design","low","")],
"Leisure, Travel & Tourism": [(RT,"Tourism","high",""),(RT,"Travel Services","high",""),(RT,"Specialty Travel","med",""),
    (RT,"Travel Ancillary Services","med",""),(RT,"Travel Media & Publications","med",""),(RE,"Vacation & Short-term Rentals","med",""),
    (WF,"Wellness Tourism","med",""),(WF,"Health & Wellness Retreats","low","")],
"Law Practice": allof(LE,"high"),
"Biotechnology": [(HC,"Biotechnology","high",""),(HC,"Medical R&D","med","")],
"Sporting Goods": [(MF,"Sporting & Athletic Goods Manufacturing","high",""),(WF,"Sporting Goods & Retail","high",""),
    (RT,"Recreational Products & Equipment","high",""),(CG,"Toys & Recreational Products","med",""),
    (RW,"Sporting Goods, Hobby, Book & Music Stores","med",""),(WF,"Fitness & Wellness Equipment","med","")],
"Primary/Secondary Education": [(ED,"Primary/Secondary Education","high","")],
"Wine and Spirits": [(CG,"Wine & Spirits","high","")],
"Public Relations and Communications": [(CS,"Corporate Communications","high",""),(CS,"Public Affairs & Lobbying","med","")],
"Security and Investigations": [(CS,"Security & Investigations","high","")],
"Online Media": [(MC,"Digital Media","high",""),(EN,"Digital & Online Media","high",""),(TE,"Digital Media & Entertainment","high",""),
    (CS,"Information Services","med",""),(MC,"Media Information Services","med",""),(MC,"Media Technology","med","")],
"Oil & Energy": [(EM,"Oil & Gas Exploration & Production","high",""),(EM,"Oil & Gas Refining & Marketing","high",""),
    (EM,"Energy Equipment & Services","high",""),(MF,"Petroleum & Coal Products Manufacturing","med",""),
    (MF,"Energy Equipment Manufacturing","med",""),(TL,"Pipeline Transportation","med","")],
"Non-Profit Organization Management": [(NP,"Nonprofit Organization Management","high",""),(NP,"Philanthropy","high",""),
    (NP,"Fundraising","high",""),(NP,"Community and Economic Development","med",""),(NP,"International Affairs & Development","med",""),
    (NP,"Healthcare and Medical Research","med",""),(NP,"Social Services","med",""),(NP,"Special Interest & Advocacy","low",""),
    (NP,"Disaster Relief & Humanitarian Aid","low",""),(NP,"Environment & Wildlife","low",""),(NP,"Health & Wellness Promotion","low","")],
"Farming": [(AG,"Agri-Tech & Digital Agriculture","low","core farming subs excluded per brief; keyword: 'agtech'"),
    (AG,"Agro-Processing","low",""),(AG,"Agricultural R&D","low",""),(AG,"Agricultural Chemicals","low","")],
"Think Tanks": [(NP,"Public Policy and Advocacy","high",""),(NP,"Science & Technology Research","med",""),
    (NP,"Education and Research","med",""),(NP,"International Affairs & Development","med","")],
"Recreational Facilities and Services": [(RT,"Attractions & Entertainment","high",""),(RT,"Outdoor Recreation","med",""),
    (WF,"Health Clubs & Community Centers","med",""),(WF,"Fitness Centers & Gyms","med",""),(EN,"Themed Entertainment","med",""),
    (EN,"Sports Entertainment","low","")],
"Medical Practice": [(HC,"Medical Practices","high",""),(HC,"Dental","high",""),(HC,"Vision Care","high",""),(HC,"Ambulatory Care","med","")],
"Market Research": [(CS,"Information Services","med","no market-research bucket; keyword: 'market research' / 'consumer insights'"),
    (CS,"R&D Services","low",""),(MC,"Media Information Services","low","")],
"Human Resources": [(CS,"Human Resources","high","FLAG: may include PEOs/HR outsourcers; Staffing & Recruiting is a separate sub and excluded"),
    (WF,"Corporate Wellness Programs","low","")],
"Publishing": [(MC,"Publishing","high","same string also under Entertainment"),(EN,"Publishing","high",""),
    (MF,"Printing & Publishing","med",""),(EN,"Literary Entertainment","low","")],
"Newspapers": [(MC,"Publishing","med","no news bucket; keyword: 'newspaper' / 'news media'"),(MC,"Digital Media","low","")],
"Mining & Metals": [(EM,"Metal Mining","high",""),(EM,"Mining & Metals Processing","high",""),(MF,"Metal Manufacturing","high","")]
    + [(EM,s,"med","field-heavy; corporate roles only") for s in ["Non-Metallic Mineral Mining","Coal Mining","Mining Support Activities",
        "Specialized Mining","Mining Equipment & Technology"]],
"Higher Education": [(ED,"Higher Education","high","")],
"Computer Networking": [(TE,"Networking & Communications","high",""),(TE,"Hardware & Equipment","med","")],
"Chemicals": [(MF,"Chemical Manufacturing","high",""),(MF,"Plastic & Rubber Manufacturing","med",""),(AG,"Agricultural Chemicals","med","")],
"Alternative Medicine": [(HC,"Alternative Medicine","high",""),(WF,"Alternative Therapies","high","")],
"Wireless": [(MC,"Telecommunications","med","keyword: 'wireless'"),(TE,"Networking & Communications","med","")],
"Veterinary": [(HC,"Veterinary","high",""),(CG,"Pet Products","low","")],
"Translation and Localization": [(CS,"Translation & Interpretation Services","high",""),(ED,"Language Education","low","")],
"Textiles": [(MF,"Textile Manufacturing","high",""),(CG,"Apparel & Textiles","med",""),(DE,"Textile Design","med","")],
"Religious Institutions": [(NP,"Religious Institutions","high","")],
"Printing": [(MF,"Printing & Publishing","high",""),(MF,"Paper Manufacturing","med","")],
"Motion Pictures and Film": [(EN,"Film & Movies","high",""),(MC,"Film & Entertainment","high",""),(AR,"Cinematic Arts","med","")],
"Industrial Automation": [(CO,"Construction Technology & Automation","med","no automation bucket; keyword: 'industrial automation' / 'robotics'"),
    (TE,"Internet of Things (IoT)","med",""),(MF,"Electrical Equipment, Appliance & Component Manufacturing","med",""),
    (MF,"Machinery Manufacturing","low","")],
"Individual & Family Services": [(NP,"Social Services","high",""),(NP,"Youth Development & Services","med",""),(HC,"Home Health Care","med","")],
"Animation": [(EN,"Animation","high",""),(DE,"Animation & 3D Design","high",""),(DE,"Motion Graphics Design","med","")],
}

# Subs left out on purpose, with reason (anything not mapped and not listed here is a bug)
EXCLUDED = {
 AG: {"Crop Production":"farmers","Animal Production":"farmers","Forestry & Logging":"field work","Fishing & Hunting":"field work",
      "Agricultural Support Activities":"farm labor services","Organic Farming":"farmers","Sustainable Agriculture":"farmers",
      "Urban Agriculture":"farmers","Agricultural Education & Training":"niche, little remote hiring"},
 AR: {"Visual Arts":"individual artists/galleries","Performing Arts":"theaters, in-person","Literary Arts":"individual writers",
      "Crafts":"makers, tiny","Art Education & Therapy":"in-person","Cultural Heritage & Preservation":"museums/government",
      "Arts Administration & Management":"arts orgs, low budget","Art Criticism & Journalism":"niche"},
 CS: {"Staffing & Recruiting":"competitor","Human Resources":"excluded by Gaston 2026-10-20 (PEO/HR-outsourcing overlap)","Executive Office":"government executive office","Outsourcing/Offshoring":"BPO/nearshore = competitor"},
 DE: {"Architecture":"Architecture & Planning (0 placements)","Landscape Design":"Architecture & Planning (0 placements)"},
 ED: {"Early Childhood Education":"daycares, in-person","Special Education":"in-person","Extracurricular Education":"in-person",
      "Environmental Education":"niche","Health & Sex Education":"niche","Religious Education":"religious schools; Religious Institutions covered via Nonprofit"},
 EN: {"Visual Arts & Exhibitions":"galleries","Comedy & Variety Entertainment":"performers","Cultural & Heritage Entertainment":"museums"},
 FI: {"Banking":"0 placements","Regulatory Bodies & Organizations":"government"},
 HC: {"Nursing & Residential Care":"nursing homes","Public Health":"government"},
 MF: {"Aerospace Manufacturing":"Defense & Space / Aviation (0 placements)","Defense Manufacturing":"Defense & Space (0 placements)",
      "Shipbuilding & Repair":"Maritime (0 placements)"},
 MC: {"Media Regulation":"government"},
 NP: {"Libraries":"public sector","Arts, Culture & Humanities":"small arts nonprofits","Civic & Social Organization":"0 placements",
      "Voluntary & Membership Organizations":"same as Civic & Social","Animal Welfare":"shelters, in-person",
      "Sports, Recreation & Leisure":"community sports orgs","Veterans & Military Support":"defense-adjacent"},
 "Public Administration": {s:"government" for s in RAW["Public Administration"]},
 "Public Safety": {s:"government/public safety" for s in RAW["Public Safety"]},
 RE: {"Senior & Assisted Living Real Estate":"nursing-home operators"},
 RW: {"Grocery Stores":"excluded by Gaston 2026-10-20 (in-store hiring)","Supermarkets":"excluded by Gaston 2026-10-20 (in-store hiring)"},
 RT: {"Education & Training in Travel & Recreation":"niche","Travel Regulation":"government"},
 TL: {"Air Transportation":"Airlines/Aviation (0 placements)","Maritime & Water Transportation":"Maritime (0 placements)"},
}

# Second pass (Gaston, 2026-10-20, revised): cut only subs where a remote role Near can place is highly unlikely.
# Every HubSpot industry with placements keeps at least one sub (except HR + Farming, which Gaston excluded).
# String-level, because the search filter is string-level.
CUT = {
 "farm / agriculture operations": ["Agro-Processing","Agricultural Machinery","Agricultural Chemicals","Farm Supplies Wholesaling",
   "Agricultural R&D","Agricultural Real Estate"],
 "extraction / commodity plant work": ["Metal Mining","Non-Metallic Mineral Mining","Coal Mining","Mining Support Activities",
   "Specialized Mining","Pipeline Transportation","Railroad Rolling Stock Manufacturing","Tobacco Manufacturing",
   "Leather & Allied Product Manufacturing","Petroleum & Coal Products Manufacturing","Nonmetallic Mineral Product Manufacturing",
   "Glass & Ceramic Manufacturing","Wood Product Manufacturing","Paper Manufacturing","Plastic & Rubber Manufacturing",
   "Metal Manufacturing","Energy Equipment Manufacturing","Heavy Machinery Manufacturing","Textile Manufacturing",
   "Apparel Manufacturing","Jewelry & Silverware Manufacturing","Modular & Prefabricated Construction"],
 "disaster relief": ["Disaster Relief & Reconstruction","Disaster Relief & Humanitarian Aid"],
 "low-fit product niche": ["Home Furnishings & Improvement","Durables & Products"],
 "fashion / craft design niche": ["Fashion Design","Packaging Design","Jewelry Design","Textile Design","Fashion & Textile Arts",
   "Fashion & Lifestyle Entertainment"],
 "in-person-only service": ["Medical & Diagnostic Labs","Nutrition & Weight Loss","Nutrition & Dietetics","Yoga & Pilates Studios",
   "Sports Training","Personal Training & Coaching","Health & Wellness Retreats","Wellness Tourism",
   "Fitness & Wellness Events & Expositions","Themed Entertainment","Transportation for Travel"],
}
CUT_REASON = {sub: r for r, subs in CUT.items() for sub in subs}
assert sum(len(v) for v in CUT.values()) == len(CUT_REASON), "duplicate in CUT"

# HubSpot industries Gaston excluded: rows stay in the CSV for coverage but feed nothing into the filter
EXCLUDED_HUBSPOT = {"Human Resources", "Farming"}

rows, included = [], {}
for hub, pairs in M.items():
    for ind, sub, conf, note in pairs:
        assert sub in RAW[ind], f"invalid: {ind} / {sub}"
        if hub in EXCLUDED_HUBSPOT:
            rows.append([hub, ind, sub, "excluded", "HubSpot industry excluded by Gaston 2026-10-20"]); continue
        if sub in CUT_REASON:
            rows.append([hub, ind, sub, "cut", f"second pass: {CUT_REASON[sub]}"]); continue
        rows.append([hub, ind, sub, conf, note])
        included.setdefault(ind, set()).add(sub)
assert len(M) == 89, len(M)

for ind, subs in RAW.items():
    for sub in subs:
        if sub in CUT_REASON and sub not in EXCLUDED.get(ind, {}):
            EXCLUDED.setdefault(ind, {})[sub] = f"second pass (Gaston 2026-10-20): {CUT_REASON[sub]}"
missing = set(CUT_REASON) - {x for v in RAW.values() for x in v}
assert not missing, missing

problems = []
for ind, subs in RAW.items():
    for s in subs:
        inc, exc = s in included.get(ind, ()), s in EXCLUDED.get(ind, {})
        if inc == exc: problems.append(f"{ind} / {s}: included={inc} excluded={exc}")
assert not problems, "\n".join(problems)

with open("industry_mapping.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["hubspot_industry","hirebase_industry","hirebase_sub_industry","confidence","note"]); w.writerows(rows)
with open("excluded_subindustries.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["hirebase_industry","hirebase_sub_industry","reason"])
    for ind, d in EXCLUDED.items():
        for s, r in d.items(): w.writerow([ind, s, r])

# Final filter: unique strings, in API order
seen, final = set(), []
for ind, subs in RAW.items():
    for s in subs:
        if s in included.get(ind, ()) and s not in seen: seen.add(s); final.append(s)
# a string excluded under one industry but included under another still ends up in the filter
clash = [s for ind,d in EXCLUDED.items() for s in d if s in seen]
open("sub_industry_filter.txt","w").write(", ".join(final) + "\n")
json.dump(final, open("sub_industry_filter.json","w"), indent=2)

total = sum(len(v) for v in RAW.values())
uniq_all = len({s for v in RAW.values() for s in v})
print(f"pairs fetched {total} | unique strings {uniq_all}")
print(f"pairs included {sum(len(v) for v in included.values())} | pairs excluded {sum(len(d) for d in EXCLUDED.values())}")
print(f"unique strings in filter {len(final)} | mapping rows {len(rows)}")
print("excluded-but-in-filter via other industry:", clash)
print("hubspot industries with nothing left in filter:", sorted({r[0] for r in rows} - {r[0] for r in rows if r[3] not in ('cut','excluded')}))
print("low:", sorted({r[0] for r in rows if r[3]=='low'} - {r[0] for r in rows if r[3] not in ('low','excluded')}))
