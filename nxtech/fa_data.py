"""
NxTech 2K26 - Failure Analysis Official Materials Data & PDF Generator Hub
Contains:
1. Part A (Circuit/Electronics) & Part B (Core/Auto-Mechanical) Problem Statements
2. Research Sources for 15 Startup Failure Case Studies
3. Startups and Their Related Research Papers
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------------------------
# 1. OFFICIAL PROBLEM STATEMENTS (CIRCUIT & CORE)
# ---------------------------------------------------------------------------

FA_PROBLEM_STATEMENTS = [
    # PART A — CIRCUIT / ELECTRONICS
    {
        "ps_id": "FA01",
        "title": "Lumos — Smart-Home IoT Switches",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate why Lumos struggled as a smart-switch hardware startup, examining customer validation, product-development costs, pricing, distribution and hardware-startup execution.",
        "research_sources": [
            "Founder account: '5 Reasons Why My IoT Startup Failed'",
            "Why Do So Many Hardware Startups Fail? — CB Insights",
            "Smart-home adoption barriers — Sustainability (2022)"
        ]
    },
    {
        "ps_id": "FA02",
        "title": "Cube26 — Consumer Technology / IoT",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate Cube26's product strategy, partnerships, monetisation and the closure of its IoT business. Distinguish closure of the IoT business from closure of the entire company.",
        "research_sources": [
            "Tiger Global-backed Cube26 shuts down IoT business — VCCircle",
            "Why Do So Many Hardware Startups Fail? — CB Insights (context)"
        ]
    },
    {
        "ps_id": "FA03",
        "title": "Log9 Materials — Battery Technology & Manufacturing",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate how battery technology choices, manufacturing scale-up, customer economics, competition, financing and commercial execution may have interacted in Log9 Materials' decline. Do not assume a specific chemistry caused the outcome without direct evidence.",
        "research_sources": [
            "The Log9 Collapse: How The Battery Tech Startup Fell From Glory — Inc42",
            "Unlocking Supply Chains for Localizing EV Battery Production in India — IISD",
            "Lithium-Ion Battery Manufacturing Landscape in India — IEEFA",
            "How Can India Indigenise Lithium-Ion Battery Cell Manufacturing? — CEEW"
        ]
    },
    {
        "ps_id": "FA04",
        "title": "Altigreen — Electric Commercial Three-Wheelers",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate the reported halt in Altigreen's manufacturing and the roles of funding, production economics, fleet adoption, demand and sales execution. Do not claim a vehicle-design defect caused the outcome without technical evidence.",
        "research_sources": [
            "Reliance-Backed Altigreen's EV Three-Wheeler Dreams Hit A Wall — Inc42",
            "Financing India's Electric Two- and Three-Wheeler Fleets — World Economic Forum"
        ]
    },
    {
        "ps_id": "FA05",
        "title": "Smartron — Smartphones & Consumer Electronics",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate how funding dependence, product competitiveness, distribution, market positioning and sustained product development affected Smartron's ability to continue operations.",
        "research_sources": [
            "Smartron — official company account",
            "Competition Issues in India's Mobile Handset Industry — ICRIER"
        ]
    },
    {
        "ps_id": "FA06",
        "title": "Play — Wearables & Smartwatches",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate whether low margins, competition, product differentiation, sourcing and distribution contributed to Play's reported market exit. Treat these as factors to test, not established causes.",
        "research_sources": [
            "Small, homebred wearables brands exit market as low margins hurt — The Economic Times",
            "India's Smartwatch Market Dipped 33% in Q1 2025 — Counterpoint Research"
        ]
    },
    {
        "ps_id": "FA07",
        "title": "Wings — Consumer Electronics & Audio",
        "category": "CIRCUIT",
        "domain": "Part A — Circuit / Electronics",
        "problem_statement": "Investigate Wings' reported market exit in relation to product differentiation, margins, sourcing and channel economics, using brand-specific evidence where available.",
        "research_sources": [
            "Small, homebred wearables brands exit market as low margins hurt — The Economic Times",
            "India's Smartwatch Market Dipped 33% in Q1 2025 — Counterpoint Research"
        ]
    },

    # PART B — CORE / AUTO-MECHANICAL
    {
        "ps_id": "FA08",
        "title": "Gensol Engineering / BluSmart EV Ecosystem",
        "category": "CORE",
        "domain": "Part B — Core / Auto-Mechanical",
        "problem_statement": "Investigate how governance, financing, regulatory compliance and operational execution affected the EV ecosystem. Frame this as a governance/business case unless direct engineering evidence supports a technical-failure claim.",
        "research_sources": [
            "Interim Order in the Matter of Gensol Engineering Limited — SEBI",
            "Gensol Engineering and BluSmart: SEBI and a governance conundrum — teaching case (DOI)"
        ]
    },
    {
        "ps_id": "FA09",
        "title": "Indian Electric Two-Wheelers — Industry-Level Case",
        "category": "CORE",
        "domain": "Part B — Core / Auto-Mechanical",
        "problem_statement": "Compare electric two-wheeler manufacturing, vehicle costs, battery requirements, adoption and compliance in India. Alternatively, narrow the study to one named manufacturer and analyse its documented outcome.",
        "research_sources": [
            "Electric two-wheeler costs and cost parity — ICCT Working Paper 2021-25",
            "Battery capacity needed to power EVs in India, 2020–2035 — ICCT",
            "Forecasting Penetration of Electric Two-Wheelers in India — NITI Aayog"
        ]
    },
    {
        "ps_id": "FA10",
        "title": "Tata Nano — Low-Cost Vehicle Concept & Commercial Outcome",
        "category": "CORE",
        "domain": "Part B — Core / Auto-Mechanical",
        "problem_statement": "Analyse how low-cost engineering trade-offs, safety and product perception, customer acceptance, production strategy and market positioning affected the Nano's commercial outcome. Do not treat fire incidents as the sole cause.",
        "research_sources": [
            "The Tata Nano: What Went Wrong? — Ivey Publishing",
            "Tata Nano to Nano Twist: The Study of Business and Marketing Challenges — Nirma University repository",
            "Tata Nano: Case of Repositioning — SAGE Journals"
        ]
    },
    {
        "ps_id": "FA11",
        "title": "Hindustan Motors / Ambassador",
        "category": "CORE",
        "domain": "Part B — Core / Auto-Mechanical",
        "problem_statement": "Investigate Ambassador's production decline through product evolution, manufacturing productivity, production costs, competition and company strategy. Separate documented operational facts from hypotheses about engineering quality.",
        "research_sources": [
            "Hindustan Motors' Struggle for Survival — ICMR case",
            "The Fall of Indian Iconic Car: The Ambassador: A Case of Marketing Myopia",
            "A Case Study of a Car whose Production has been Wound-Up: Ambassador"
        ]
    },
    {
        "ps_id": "FA12",
        "title": "Mahindra Reva — Early Electric-Car Innovation & Adoption",
        "category": "CORE",
        "domain": "Part B — Core / Auto-Mechanical",
        "problem_statement": "Examine the market limitations of the early REVA, including range, charging access, price, performance, consumer acceptance and commercialisation strategy. Define the specific outcome rather than labelling the whole company a failure.",
        "research_sources": [
            "REVA Electric Car: A Case Study of Innovation at RECC — Inderscience",
            "Innovation in the Midst of Uncertainty: Mahindra Reva Electric Vehicles — IIM Ahmedabad case",
            "Should Mahindra Reva Strengthen Its Market Position in India? — Harvard Business Publishing"
        ]
    }
]

# ---------------------------------------------------------------------------
# 2. RESEARCH SOURCES FOR 15 STARTUP FAILURE CASE STUDIES
# ---------------------------------------------------------------------------

STARTUP_SOURCES_DATA = [
    {
        "id": 1,
        "name": "BYJU'S",
        "domain": "EdTech",
        "status_note": "Insolvency proceedings are live; sale process and disputed creditor claims are ongoing.",
        "sources": [
            ("Byju's insolvency saga deepens as Supreme Court issues notice", "Storyboard18 (May 2025)", "Legal timeline of insolvency appeals and BCCI withdrawal dispute."),
            ("NCLAT did not apply its mind while closing insolvency proceedings: SC", "Bar & Bench", "Court reasoning and Glas Trust challenge over $1.2B term loan."),
            ("Byju Raveendran back in control as NCLAT accepts settlement", "Storyboard18 (2024)", "First admission into insolvency and the settlement reversing it."),
            ("Aditya Birla Finance, Glas Trust move NCLT to replace RP", "Bar & Bench", "Creditor conflict and resolution governance process."),
            ("NCLT stays Byju's bidding process till next hearing", "YourStory (July 2026)", "Most recent status: sale process & disputed creditor claims.")
        ]
    },
    {
        "id": 2,
        "name": "BitConnect",
        "domain": "Cryptocurrency / Blockchain",
        "status_note": "Founders charged by US DOJ and SEC in alleged $2.4B Ponzi scheme; cite DOJ and SEC official releases.",
        "sources": [
            ("BitConnect's Kumbhani Charged by U.S. in $2.4B Ponzi Scam", "Bloomberg Law (Feb 2022)", "Summary of DOJ indictment and criminal charges."),
            ("BitConnect founder indicted for alleged $2.4 billion Ponzi scheme", "The Block (Feb 2022)", "Mechanics of lending program and automated trading-bot claims."),
            ("SEC Charges Global Crypto Lending Platform in Ponzi-Like Scheme", "Davis Wright Tremaine (2021)", "Regulatory and securities-law analysis of SEC action."),
            ("Federal Grand Jury Indicts BitConnect Founder Over $2.4B Scheme", "Merkle Science", "Timeline linking SEC action (2021) to DOJ indictment (2022)."),
            ("BitConnect, Satish Kumbhani & Glenn Arcaro sued by SEC", "BehindMLM", "Referral/MLM structure and corporate shell entities.")
        ]
    },
    {
        "id": 3,
        "name": "WhiteHat Jr",
        "domain": "EdTech",
        "status_note": "Acquired by BYJU'S for $300M in 2020; faced extreme customer acquisition costs and subsequent mass downsizing.",
        "sources": [
            ("Byju's has discussed shutting down coding platform WhiteHat Jr", "TechCrunch (Feb 2023)", "Core report on the $300M acquisition and closure talks."),
            ("BYJU'S Mulls Closing Down Its Loss Making Entity WhiteHat Jr", "Inc42", "Monthly cash burn and contribution to parent company losses."),
            ("Ever since acquisition, WhiteHat Jr in news for wrong reasons", "Scroll.in (2020)", "Aggressive marketing claims, criticism, and defamation suits."),
            ("Byju's is stuck with WhiteHat Jr", "The Morning Context", "Acquisition integration bottlenecks after pandemic surge."),
            ("Byju's cuts 600 jobs as edtech space shrinks in India", "Deccan Herald", "Layoffs and structural market contraction.")
        ]
    },
    {
        "id": 4,
        "name": "Hike",
        "domain": "Social Media / Messaging",
        "status_note": "Tencent & SoftBank-backed; shutdown of core Sticker Chat messenger due to network effects; pivoted to gaming apps.",
        "sources": [
            ("Tencent-backed Hike gives up on messaging", "TechCrunch (Jan 2021)", "Shutdown announcement, valuation history, and product pivot."),
            ("WhatsApp rival Hike goes off the air in India", "Deccan Herald / Bloomberg", "Founder's analysis of global network effects in messaging."),
            ("Hike taken down from Google Play Store & Apple App Store", "YourStory (Jan 2021)", "Funding history ($260M+) and Rush replacement products."),
            ("Hike narrows FY20 net loss to Rs 180.75 crore", "exchange4media", "Revenue vs. expenditure and structural sustainability gap."),
            ("WhatsApp competitor Hike Sticker Chat is shutting down", "TechRadar", "Engagement metrics and user retention drop-off.")
        ]
    },
    {
        "id": 5,
        "name": "Dunzo",
        "domain": "Hyperlocal / Quick Commerce",
        "status_note": "App went offline in Jan 2025; Reliance wrote off its $200M investment; cash-intensive quick-commerce burn.",
        "sources": [
            ("Dunzo goes offline as investors, co-founder depart", "YourStory (Jan 2025)", "Immediate trigger: app outage and leadership departures."),
            ("Dunzo goes offline after cofounder joins Flipkart", "Business Today (Jan 2025)", "Funding history ($450M+) and sequential fleet downsizing."),
            ("Reliance writes off its $200M investment in Dunzo", "YourStory (Aug 2025)", "Capital write-off and unsustainable delivery unit economics."),
            ("Dunzo's Downfall Explained: Reliance write-off analysis", "Outlook Business", "Co-founder exits, unpaid salaries, and investor veto barriers."),
            ("Reliance Retail steps away from Dunzo funding talks", "Retail Insight Network", "Distress sale valuation drop and hyper-competition from Zepto.")
        ]
    },
    {
        "id": 6,
        "name": "BluSmart",
        "domain": "EV Mobility / CleanTech",
        "status_note": "Suspended operations in Apr 2025 amid SEBI regulatory inquiry into related entity Gensol Engineering.",
        "sources": [
            ("BluSmart suspends operations as SEBI investigates co-founder", "Scroll.in / Reuters (Apr 2025)", "Suspension, driver impacts, and SEBI internal control findings."),
            ("BluSmart appears to suspend service in wake of EV loan probe", "TechCrunch (Apr 2025)", "Inter-company linkages between Gensol and BluSmart fleet."),
            ("Under SEBI Lens, Jaggi Brothers Resign From Gensol", "Inc42 (2025)", "SEBI interim orders, ED inquiries, and founder resignations."),
            ("Crisis-Hit BluSmart's App Breaks Down", "Inc42 (2025)", "Fleet grounding following credit and working-capital freeze."),
            ("BluSmart EV taxi service shuts after SEBI reveals fraud", "Law.asia", "Regulatory compliance and corporate-governance audit.")
        ]
    },
    {
        "id": 7,
        "name": "GoMechanic",
        "domain": "AutoTech / Car Servicing",
        "status_note": "Founder admitted to accounting irregularities in Jan 2023; assets acquired in distress sale by Lifelong Group.",
        "sources": [
            ("GoMechanic cooked books; founder admits grave errors", "Outlook Business (Jan 2023)", "Founder's public admission and 70% workforce downsizing."),
            ("GoMechanic's Financial Audit: Lessons for startups", "Outlook Business (Jan 2023)", "Audit discrepancies and growth-at-all-costs culture."),
            ("GoMechanic Modus Operandi: Founder Fraud Laid Bare in FIR", "Inc42", "Forensic findings of fictitious garages and diverted funds."),
            ("GoMechanic acquired by auto parts maker Lifelong Group", "YourStory (Mar 2023)", "Distressed-sale resolution and asset takeover terms."),
            ("GoMechanic: A cautionary tale for startup due diligence", "Business Today (Mar 2023)", "Investor due diligence breakdown and forensic recovery lessons.")
        ]
    },
    {
        "id": 8,
        "name": "Vogo",
        "domain": "Mobility / Scooter Rentals",
        "status_note": "Asset-heavy two-wheeler rental model; acquired by Chalo in share swap deal after FY22 losses.",
        "sources": [
            ("Vogo's acquisition by Chalo and FY22 financials", "Entrackr", "Share-swap terms, FY22 loss of Rs 73.4 Cr, unit economics."),
            ("Ola-Backed Vogo Spent 94X More In FY19 to Rev Up Growth", "Inc42", "Asset-heavy fleet depreciation and maintenance expenditure."),
            ("Can Vogo Take Bike Rental to an Electric Future?", "Inc42 Interview", "Per-km rental pricing models and electric transition costs."),
            ("Vogo raises $19M Series C to take on Bounce", "Entrepreneur India", "Capital-intensity race in shared two-wheeler micromobility."),
            ("How bike rental platform Vogo tapped IoT for scale", "YourStory (July 2020)", "Fleet hardware maintenance, vandalism, and IoT tracking.")
        ]
    },
    {
        "id": 9,
        "name": "PepperTap",
        "domain": "E-Commerce / Grocery Delivery",
        "status_note": "Raised $51M; shut down B2C grocery delivery in April 2016 due to heavy discounting and logistics costs.",
        "sources": [
            ("PepperTap's collapse shows what went wrong with e-grocers", "Quartz (2016)", "Discount-driven customer acquisition with negative unit margins."),
            ("PepperTap scales back service in six cities", "TechCrunch (Feb 2016)", "Losses per delivery and geographic consolidation."),
            ("PepperTap to shut down operations this month", "YourStory (Apr 2016)", "CEO confirmation of B2C shutdown and shift to logistics."),
            ("PepperTap shuts grocery, pivots to logistics", "MediaNama (Apr 2016)", "Funding history ($51M) and systemic burn in early hyperlocal."),
            ("PepperTap scaled fast, raised $50M, then shut down", "e27 (Apr 2016)", "Order volume economics and warehouse-less inventory limits.")
        ]
    },
    {
        "id": 10,
        "name": "Stayzilla",
        "domain": "TravelTech / Homestays",
        "status_note": "Raised $34M; halted operations in Feb 2017 amid severe vendor disputes and capital depletion.",
        "sources": [
            ("Lessons for startups from the Stayzilla saga", "Business Today (Mar 2017)", "High burn on customer incentives and market mismatch."),
            ("Top controversies that shook the startup ecosystem", "Inc42 (Dec 2017)", "Chronology of suspension, vendor dispute, and founder arrest."),
            ("The Ides of March strikes Stayzilla", "YourStory (Mar 2017)", "The vendor litigation dispute and founder's statement."),
            ("Stayzilla Had Zero Intent to Pay: Creditor View", "Entrepreneur India", "Vendor advertising payment defaults and working capital crisis."),
            ("Yogendra Vasupal – The Rise and Fall of Stayzilla", "ICMR Case Studies (2018)", "Business-school case study on scale, unit margins, and burn.")
        ]
    },
    {
        "id": 11,
        "name": "Doodhwala",
        "domain": "FoodTech / Milk Subscription",
        "status_note": "Suspended deliveries in Oct 2019; vendor payment defaults; customer database transitioned to FreshToHome.",
        "sources": [
            ("Doodhwala Vendors File FIR for Unpaid Dues", "Inc42 (Nov 2019)", "Scale of vendor dues (Rs 6-7 Cr) and working-capital depletion."),
            ("Doodhwala Employees File FIR Over Unpaid Salaries", "Inc42 (2019)", "Failed bridge round and rapid operations wind-down."),
            ("Milk delivery startup Doodhwala suspends services", "DealStreetAsia (2019)", "Metropolitan delivery economics and low average order value."),
            ("Doodhwala redirects customers to FreshToHome app", "OfficeChai (2019)", "Wallet balance transfers and customer handover."),
            ("Doodhwala stops operations; FreshToHome serves customers", "Entrackr (2019)", "Micro-delivery logistics unit economics and cold-chain costs.")
        ]
    },
    {
        "id": 12,
        "name": "Koinex",
        "domain": "Crypto / FinTech Exchange",
        "status_note": "Shut down in June 2019 due to RBI circular restricting commercial banking access to crypto businesses.",
        "sources": [
            ("Koinex shuts down amidst regulatory uncertainty", "The Block (June 2019)", "Closure announcement and banking support withdrawal."),
            ("Crypto Exchange Koinex Falls Prey to India's Ban", "Inc42 (June 2019)", "Founder's exit statement and payment gateway disruption."),
            ("Koinex shuts down after months of disruption", "MediaNama (June 2019)", "Impact on peer exchanges and pending Supreme Court petition."),
            ("Koinex shuts operations citing banking uncertainty", "YourStory (June 2019)", "Customer fiat refund process and timeline of shutdown."),
            ("Supreme Court strikes down RBI banking ban", "The Block (March 2020)", "Subsequent legal victory setting aside the RBI circular.")
        ]
    },
    {
        "id": 13,
        "name": "Lumos",
        "domain": "Smart-Home Electronics / IoT",
        "status_note": "Hardware IoT startup failed in 2014-15; founders published detailed post-mortem on hardware unit economics.",
        "sources": [
            ("Lumos — Startup Cemetery Case", "Failory", "Co-founders' realization on hardware engineering execution barriers."),
            ("4 reasons a great startup idea is not enough", "e27 (Sept 2015)", "Founder quotes on component pricing, tooling, and minimum orders."),
            ("8 high-profile Asian startup shutdowns of 2015", "e27 (Dec 2015)", "IoT hardware startup failure context and supply-chain delays."),
            ("These 12 startups died in Q2 — here's why", "VentureBeat", "Failed distribution pivots and hardware manufacturing costs."),
            ("Lumos — IoT startup postmortem learnings", "Alexander Jarvis Blog", "Key execution lessons from founder's post-mortem analysis.")
        ]
    },
    {
        "id": 14,
        "name": "Mojocare",
        "domain": "HealthTech / Wellness",
        "status_note": "Board decided to wind down in 2023 following forensic audit inquiries into reported revenue figures.",
        "sources": [
            ("Mojocare investors uncover financial irregularities", "TechCrunch (June 2023)", "Investor statement on inflated revenue and business model viability."),
            ("VCs Flag Financial Irregularities at Mojocare", "Inc42 (2023)", "Fundraising history ($20.6M) and capital deployment analysis."),
            ("Mojocare Board Discusses Winding Down Business", "Inc42 (July 2023)", "Forensic audit review and capital return to investors."),
            ("Mojocare lays off 170 employees within a year of funding", "Entrackr (June 2023)", "Scale of staff layoffs and operations contraction."),
            ("Mojocare plans shutdown amid governance issues", "MediaNama (July 2023)", "Investor audit conclusions and lack of acquisition interest.")
        ]
    },
    {
        "id": 15,
        "name": "Crejo.Fun",
        "domain": "EdTech / Extracurricular Learning",
        "status_note": "Matrix-backed extracurricular edtech; shut down mid-2022 following post-pandemic offline school reopening.",
        "sources": [
            ("Matrix-Backed Crejo.Fun Shuts Down; Failed to Raise Funding", "Inc42 (2022)", "Post-lockdown demand drop for online children's extracurriculars."),
            ("Crejo.Fun raises $3M led by Matrix Partners, 021 Capital", "YourStory (June 2021)", "Initial funding thesis for age 4-14 creative online learning."),
            ("Crejo.Fun raises $3M seed funding", "Matrix Partners India", "Original investment thesis and pandemic-era digital growth."),
            ("FrontRow Winds Up Operations in Extracurricular Space", "Inc42 (2023)", "Peer comparison showing structural headwinds across sector."),
            ("Edtech Downfall Continues: Sector-Wide Review", "Inc42 (2023)", "Funding winter analysis and systemic drop in paid subscriptions.")
        ]
    }
]

# ---------------------------------------------------------------------------
# 3. STARTUPS AND THEIR RELATED RESEARCH PAPERS
# ---------------------------------------------------------------------------

STARTUP_PAPERS_DATA = [
    {
        "id": 1,
        "name": "BYJU'S",
        "domain": "EdTech",
        "description": "Indian online learning company known for video lessons and personalised learning apps. Underwent a high-profile insolvency process.",
        "paper_title": "The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring",
        "paper_citation": "Benjamin S. Bloom · Educational Researcher, vol. 13(6), 1984",
        "relation_type": "Closely Related",
        "relation_detail": "Shows that one-to-one tutoring with mastery learning beats classroom teaching by 2 standard deviations and explores how to deliver that at scale, the foundational premise of personalized EdTech."
    },
    {
        "id": 2,
        "name": "BitConnect",
        "domain": "Cryptocurrency / Blockchain",
        "description": "Crypto lending and trading-bot platform alleged by US authorities to be a $2.4B Ponzi scheme; collapsed in 2018.",
        "paper_title": "Analyzing the Bitcoin Ponzi Scheme Ecosystem",
        "paper_citation": "Marie Vasek, Tyler Moore · Financial Cryptography Workshops, 2018",
        "relation_type": "Closely Related",
        "relation_detail": "Empirically measures how Bitcoin-based Ponzi schemes operate, attract user deposits, and inevitably collapse, mirroring BitConnect's structural trajectory."
    },
    {
        "id": 3,
        "name": "WhiteHat Jr",
        "domain": "EdTech",
        "description": "Online coding classes for children, acquired by BYJU'S for ~$300M in 2020. Faced high marketing claims and subsequent restructuring.",
        "paper_title": "Scratch: Programming for All (author's version: 'Scratch: Programming for Everyone')",
        "paper_citation": "Mitchel Resnick et al. · Communications of the ACM, vol. 52(11), 2009",
        "relation_type": "Closely Related",
        "relation_detail": "Explains the foundational design and pedagogical principles behind teaching visual programming to young learners (ages 8-16), WhiteHat Jr's target customer segment."
    },
    {
        "id": 4,
        "name": "Hike",
        "domain": "Social Media / Messaging",
        "description": "Indian messaging app (Sticker Chat) backed by Tencent and SoftBank. Shut the messenger in Jan 2021 and pivoted to other digital products.",
        "paper_title": "Network Externalities, Competition, and Compatibility",
        "paper_citation": "Michael L. Katz, Carl Shapiro · American Economic Review, vol. 75(3), 1985, pp. 424–440",
        "relation_type": "Closely Related",
        "relation_detail": "The foundational economic theory of network effects: communication platform utility scales quadratically with user base; cited by Hike's founder upon sunsetting the messenger."
    },
    {
        "id": 5,
        "name": "Dunzo",
        "domain": "Hyperlocal / Quick Commerce",
        "description": "Bengaluru-based on-demand quick-commerce app. Went offline in Jan 2025 following unsustainable burn and stakeholder write-offs.",
        "paper_title": "Dynamic Pickup and Delivery Problems",
        "paper_citation": "Gerardo Berbeglia, Jean-François Cordeau, Gilbert Laporte · European Journal of Operational Research, vol. 202(1), 2010",
        "relation_type": "Closely Related",
        "relation_detail": "Surveys real-time dynamic routing and vehicle fleet assignment for on-demand delivery, the core mathematical challenge governing hyperlocal unit economics."
    },
    {
        "id": 6,
        "name": "BluSmart",
        "domain": "EV Mobility / CleanTech",
        "description": "All-electric ride-hailing service in Indian metros. Suspended operations in April 2025 amid regulatory investigations.",
        "paper_title": "Optimization of Charging Infrastructure for Electric Taxis",
        "paper_citation": "Transportation Research Record, vol. 2416, 2014, pp. 82–91",
        "relation_type": "Closely Related",
        "relation_detail": "Models optimal fast-charging hub sizing, location algorithms, and grid infrastructure costs critical to sustaining high-utilization commercial EV fleets."
    },
    {
        "id": 7,
        "name": "GoMechanic",
        "domain": "AutoTech / Car Servicing",
        "description": "Two-sided workshop aggregator platform. Faced forensic audit inquiries over accounting practices and was sold in 2023.",
        "paper_title": "Platform Competition in Two-Sided Markets",
        "paper_citation": "Jean-Charles Rochet, Jean Tirole · Journal of the European Economic Association, vol. 1(4), 2003",
        "relation_type": "Closely Related",
        "relation_detail": "Nobel laureate economic model governing how two-sided platforms (car owners vs. independent mechanics) set cross-subsidies, pricing, and quality certification."
    },
    {
        "id": 8,
        "name": "Wave Computing",
        "domain": "Semiconductors / AI Processor Cores",
        "description": "US AI chipmaker that developed a dataflow architecture from clockless processing elements. Reorganized through Chapter 11 and emerged as MIPS.",
        "paper_title": "NULL Convention Logic: A Complete and Consistent Logic for Asynchronous Digital Circuit Synthesis",
        "paper_citation": "Karl M. Fant, Scott A. Brandt · ASAP Conference, 1996 & Wave White Paper",
        "relation_type": "Basis",
        "relation_detail": "Direct technological foundation: Wave co-founder Karl Fant co-invented NULL Convention Logic (NCL), and Wave's DPU architecture was directly built upon asynchronous clockless CGRA circuits."
    },
    {
        "id": 9,
        "name": "PepperTap",
        "domain": "E-Commerce / Grocery Delivery",
        "description": "Early Indian online grocery delivery app that raised $51M before shutting its consumer delivery division in 2016.",
        "paper_title": "Incentive Schemes for Attended Home Delivery Services",
        "paper_citation": "Ann Melissa Campbell, Martin Savelsbergh · Transportation Science, vol. 40(3), 2006",
        "relation_type": "Closely Related",
        "relation_detail": "Analyzes dynamic delivery pricing incentives to optimize slot distribution and eliminate negative gross margins in scheduled urban grocery fulfillment."
    },
    {
        "id": 10,
        "name": "Stayzilla",
        "domain": "TravelTech / Homestays",
        "description": "Chennai-based homestay marketplace that raised $34M before halting operations in 2017 amid severe working capital constraints.",
        "paper_title": "The Rise of the Sharing Economy: Estimating the Impact of Airbnb on the Hotel Industry",
        "paper_citation": "Georgios Zervas, Davide Proserpio, John W. Byers · Journal of Marketing Research, 2017",
        "relation_type": "Closely Related",
        "relation_detail": "Analyzes the dynamics of peer-to-peer homestay platforms competing with traditional hospitality networks and the challenges of decentralized quality control."
    },
    {
        "id": 11,
        "name": "Doodhwala",
        "domain": "FoodTech / Milk Subscription",
        "description": "Subscription milk and essentials daily micro-delivery startup that ceased operations in Oct 2019 due to logistics unit economic constraints.",
        "paper_title": "Perishable Inventory Theory: A Review",
        "paper_citation": "Steven Nahmias · Operations Research, vol. 30(4), 1982, pp. 680–708",
        "relation_type": "Closely Related",
        "relation_detail": "Surveys mathematical inventory models for highly perishable stock with strict shelf-life constraints, directly governing the supply chain of morning dairy delivery."
    },
    {
        "id": 12,
        "name": "Koinex",
        "domain": "Crypto / FinTech Exchange",
        "description": "Prominent Indian digital assets exchange that halted operations in June 2019 citing banking rail closures under central bank circulars.",
        "paper_title": "Beware the Middleman: Empirical Analysis of Bitcoin-Exchange Risk",
        "paper_citation": "Tyler Moore, Nicolas Christin · Financial Cryptography and Data Security, 2013",
        "relation_type": "Closely Related",
        "relation_detail": "Empirically assesses systemic operational, regulatory, and banking interface risks inherent in centralized cryptocurrency exchange operations."
    },
    {
        "id": 13,
        "name": "Lumos",
        "domain": "Smart-Home Electronics / IoT",
        "description": "Hardware startup manufacturing learning smart switches to automate appliances; ceased operations after manufacturing cost escalation.",
        "paper_title": "The Neural Network House: An Environment that Adapts to its Inhabitants",
        "paper_citation": "Michael C. Mozer · AAAI Spring Symposium Technical Report SS-98-02, 1998",
        "relation_type": "Closely Related",
        "relation_detail": "Pioneering academic architecture for automated residential energy management that infers inhabitant patterns from sensors, the conceptual model of Lumos switches."
    },
    {
        "id": 14,
        "name": "Mojocare",
        "domain": "HealthTech / Wellness",
        "description": "Digital clinic focusing on specialized wellness care that wound down in 2023 following forensic financial review.",
        "paper_title": "Recommendations from the 2023 International Evidence-based Guideline for PCOS",
        "paper_citation": "Helena J. Teede et al. · Human Reproduction, vol. 38(9), 2023, pp. 1655–1679",
        "relation_type": "Closely Related",
        "relation_detail": "International evidence-based clinical diagnostic and management framework for polycystic ovary syndrome, one of the central conditions targeted by Mojocare's care plans."
    },
    {
        "id": 15,
        "name": "Crejo.Fun",
        "domain": "EdTech / Extracurricular Learning",
        "description": "Matrix-backed online live extracurricular platform for children (ages 4-14) that ceased operations following school reopenings.",
        "paper_title": "Extracurricular Activities and Adolescent Development",
        "paper_citation": "Jacquelynne S. Eccles et al. · Journal of Social Issues, vol. 59(4), 2003",
        "relation_type": "Closely Related",
        "relation_detail": "Longitudinal developmental study analyzing how structured extracurricular programs shape cognitive development, social identity, and academic achievement."
    }
]

# ---------------------------------------------------------------------------
# REPORTLAB PDF GENERATOR FUNCTIONS
# ---------------------------------------------------------------------------

def _create_base_doc(buffer, title_str):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    heading_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    return doc, styles, title_style, sub_style, heading_style


def generate_fa_statements_pdf_bytes():
    """Generates Doc 1: Problem Statements & Research Paper Links (Circuit & Core Auto)."""
    buffer = io.BytesIO()
    doc, styles, title_style, sub_style, heading_style = _create_base_doc(
        buffer, "NxTech 2K26 - Failure Analysis Problem Statements"
    )

    story = [
        Paragraph("<b>STUDENT RESEARCH COUNCIL (SRC)</b>", title_style),
        Paragraph("Dr. Mahalingam College of Engineering & Technology, Pollachi", sub_style),
        Spacer(1, 4),
        Paragraph("<b>NxTech 2K26 — Failure Analysis Problem Statements & Research Paper Links</b>", ParagraphStyle(
            'Banner', parent=title_style, fontSize=11, leading=14, textColor=colors.HexColor('#7C1A7E')
        )),
        Paragraph("Forensic Engineering Case Defense • Circuit / Electronics & Core / Auto-Mechanical Tracks", sub_style),
        Spacer(1, 10),
    ]

    th_style = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=1)
    id_style = ParagraphStyle('ID', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#7C1A7E'), alignment=1)
    body_title = ParagraphStyle('BT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#0F172A'))
    body_desc = ParagraphStyle('BD', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#334155'))
    sources_style = ParagraphStyle('BS', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#475569'))
    track_style = ParagraphStyle('TR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.HexColor('#1E293B'), alignment=1)

    headers = [
        Paragraph("PS ID", th_style),
        Paragraph("Case Topic & Problem Statement", th_style),
        Paragraph("Track", th_style),
        Paragraph("Key Research Sources / References", th_style),
    ]
    data = [headers]

    for item in FA_PROBLEM_STATEMENTS:
        case_content = [
            Paragraph(f"<b>{item['title']}</b>", body_title),
            Spacer(1, 2),
            Paragraph(item['problem_statement'], body_desc)
        ]
        sources_list = [Paragraph(f"• {s}", sources_style) for s in item['research_sources']]

        row = [
            Paragraph(f"<b>{item['ps_id']}</b>", id_style),
            case_content,
            Paragraph(item['domain'].replace("Part ", "Pt "), track_style),
            sources_list
        ]
        data.append(row)

    col_widths = [45, 230, 95, 170]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))

    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_fa_sources_pdf_bytes():
    """Generates Doc 2: Research Sources for 15 Startup Failure Case Studies."""
    buffer = io.BytesIO()
    doc, styles, title_style, sub_style, heading_style = _create_base_doc(
        buffer, "NxTech 2K26 - 15 Startup Case Studies Research Sources"
    )

    story = [
        Paragraph("<b>STUDENT RESEARCH COUNCIL (SRC)</b>", title_style),
        Paragraph("Dr. Mahalingam College of Engineering & Technology, Pollachi", sub_style),
        Spacer(1, 4),
        Paragraph("<b>Research Sources for 15 Startup Failure Case Studies</b>", ParagraphStyle(
            'Banner', parent=title_style, fontSize=11, leading=14, textColor=colors.HexColor('#0F172A')
        )),
        Paragraph("Curated Reference Material for NxTech 2K26 Failure Analysis Challenge", sub_style),
        Spacer(1, 10),
    ]

    th_style = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    src_title = ParagraphStyle('ST', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.HexColor('#0F172A'))
    src_pub = ParagraphStyle('SP', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#64748B'))
    src_use = ParagraphStyle('SU', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#334155'))
    case_header_style = ParagraphStyle('CH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0F172A'))
    note_style = ParagraphStyle('CN', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#7C1A7E'))

    for c in STARTUP_SOURCES_DATA:
        case_flow = []
        case_flow.append(Spacer(1, 6))
        case_flow.append(Paragraph(f"<b>{c['id']}. {c['name']}</b> <font color='#64748B' size='8'>({c['domain']})</font>", case_header_style))
        case_flow.append(Spacer(1, 3))

        headers = [Paragraph("#", th_style), Paragraph("Source Document & Publication", th_style), Paragraph("Useful Research Context", th_style)]
        rows = [headers]
        for s_idx, (title, pub, use) in enumerate(c['sources'], start=1):
            source_cell = [
                Paragraph(title, src_title),
                Spacer(1, 1),
                Paragraph(pub, src_pub)
            ]
            rows.append([
                Paragraph(str(s_idx), src_use),
                source_cell,
                Paragraph(use, src_use)
            ])

        t = Table(rows, colWidths=[20, 290, 230])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        case_flow.append(t)
        case_flow.append(Spacer(1, 2))
        case_flow.append(Paragraph(f"<b>Status note:</b> {c['status_note']}", note_style))
        story.append(KeepTogether(case_flow))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_fa_papers_pdf_bytes():
    """Generates Doc 3: Startups and Their Related Research Papers."""
    buffer = io.BytesIO()
    doc, styles, title_style, sub_style, heading_style = _create_base_doc(
        buffer, "NxTech 2K26 - Startups and Related Research Papers"
    )

    story = [
        Paragraph("<b>STUDENT RESEARCH COUNCIL (SRC)</b>", title_style),
        Paragraph("Dr. Mahalingam College of Engineering & Technology, Pollachi", sub_style),
        Spacer(1, 4),
        Paragraph("<b>Startups and Their Related Research Papers</b>", ParagraphStyle(
            'Banner', parent=title_style, fontSize=11, leading=14, textColor=colors.HexColor('#7C1A7E')
        )),
        Paragraph("15 Startup Failure Case Studies Paired with Theoretical Academic Research Foundations", sub_style),
        Spacer(1, 10),
    ]

    th_style = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    st_title = ParagraphStyle('ST', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#0F172A'))
    st_desc = ParagraphStyle('SD', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#475569'))
    pp_title = ParagraphStyle('PT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#1E293B'))
    pp_cit = ParagraphStyle('PC', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor('#64748B'))
    rel_type = ParagraphStyle('RT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#7C1A7E'))
    rel_desc = ParagraphStyle('RD', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#334155'))

    headers = [
        Paragraph("#", th_style),
        Paragraph("Startup & Overview", th_style),
        Paragraph("Academic Research Paper", th_style),
        Paragraph("Relation & Forensic Analysis", th_style)
    ]
    data = [headers]

    for p in STARTUP_PAPERS_DATA:
        startup_cell = [
            Paragraph(f"<b>{p['name']}</b> ({p['domain']})", st_title),
            Spacer(1, 1),
            Paragraph(p['description'], st_desc)
        ]
        paper_cell = [
            Paragraph(p['paper_title'], pp_title),
            Spacer(1, 1),
            Paragraph(p['paper_citation'], pp_cit)
        ]
        relation_cell = [
            Paragraph(f"<b>{p['relation_type']}</b>", rel_type),
            Spacer(1, 1),
            Paragraph(p['relation_detail'], rel_desc)
        ]
        data.append([
            Paragraph(str(p['id']), st_title),
            startup_cell,
            paper_cell,
            relation_cell
        ])

    col_widths = [18, 145, 175, 202]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
