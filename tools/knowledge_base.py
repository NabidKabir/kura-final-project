# The KNOWLEDGE_BASE is a dictionary that will store all of the static information for our database. It is the page information rather than the url. This allows the research agent to look for specific information. it is very important that the agent does not just look for info from the web, especially because these are laws and regulations that can result in fines. 

KNOWLEDGE_BASE = {
    "nyc": {
        "sanitation_businesses_overview": """ We conduct research and create policies that govern when, where, and how businesses separate and set out their waste. Although we do not provide businesses with collection services, they must comply with the NYC Department of Sanitation (DSNY) rules and regulations. All businesses in NYC must hire a private carter licensed with the Business Integrity Commission (BIC) for the collection of trade waste. DSNY does not provide collection services for businesses in most cases.""",
        
        "business_containerization": """ As of March 1, 2024, all businesses in NYC must use bins with secure lids when setting out trash for collection. 

    This rule applies to every business in New York City, regardless of what is sold. Any trash or organics (food waste, food-soiled paper, plant waste) must be in a bin with a secure lid. This requirement does not apply to businesses that have waste collected from a loading dock. This rule does not require the separation of trash and organics, only the use of bins with secure lids for collection. However, some businesses are required to separate their organic waste.""",
    
    "setout_times": """ All businesses must use a bin with a secure lid for trash. Bins may be placed at the curb 1 hour before closing or after 8 PM. Bins can also be used for recycling, but it is not required. Recycling in bags or bundles can be set out after 8 PM. All bins must be removed from the curb by the time the business reopens. Place bins with secure lids at the curb 1 hour before closing or after 8:00 PM. You may also use bins for recycling, but it is not required. Recycling in bags or bundles can be set out after 8:00 PM. This does not apply to businesses that have waste collected from a loading dock. Bins must be removed from the curb by the time your business reopens""",
    
    "separate_and_setout": """ All trash, food, and food-soiled paper must be in a bin with a secure lid when set out at the curb for collection. Businesses must have enough bins to contain waste generated in a 72-hour period. Failure to comply may result in fines. The requirement does not apply to recyclables (metal, glass, plastic, or clean paper and cardboard). This rule does not require the separation of trash from food or food-soiled paper — it only requires that these materials be placed in bins with secure lids for collection. NOTE: Businesses required to source-separate organics under Local Law 146 of 2013 must continue to do so by placing their food waste in a separate bin with a secure lid. Trash must be set out in a separate bin from food and food-soiled paper. Find out if commercial organics requirements apply to you.""" ,
    
    "dumpster_usage_and_setout": """ If trash is picked up using metal dumpsters, the containers must be: Removed immediately after collection. If the collection service occurs overnight and a responsible party is not present, a reasonable amount of time (about an hour) is allowed for the removal of containers once the responsible party is on premise. Removed from sidewalks/streets and placed inside or in the rear of the of the building. Maintained in a neat, clean, and closed condition at all times, and the area around them must also remain neat and clean.""" ,
    
    "bin_storage": """Bins should be stored inside or in a rear yard if possible, when not set out for collection. If space is not available, bins can be stored within three (3) feet of the building line. Bins (including dumpsters) must be covered at all times with securely fitting covers/lids. Bins must be maintained in a neat and orderly manner and always allow for a clear path of pedestrian travel on the sidewalk. Enclosures on the sidewalk are subject to DOT regulations. """,
    
    
    "source_separated_recycling": """ Source-separated recycling requires businesses to separate waste into two "streams" (groups). 
Metal, glass, plastic, and beverage cartons
Paper and cardboard
The two streams must be kept separate from trash at all times. 

If customers/staff place all recycling into one bin during normal business operations, staff must then separate and sort the material into the two streams, store them separately, and set out for collection in separate bins. 

The private carter is then required to collect each stream in a separate truck or place them in separate compartments of a truck. Trash must be collected by a separate truck from recycling.

Businesses that are source-separating recycling are required to post an official BIC decal with the name and license number of the private carter, and must indicate the types of recyclables being collected.
""",

"co-collection_recycling": """ Co-collection allows private carters to collect source-separated recycling in one truck. Trash must be collected in a separate truck or in a compartment separate from recyclables. Businesses using a private carter authorized for co-collection of recyclables must source-separate their recycling (see above) and set recycling streams out for collection in separate bins/bags. Cardboard can be baled/bundled. 

Businesses are required to post an official BIC decal indicating that co-collection is used and including the name and license number of the private carter that is authorized to co-collect recyclables.""",

"single_stream_recycling": """ Single-stream recycling allows businesses to collect, store, and set out all recyclable material (metal, glass, plastic, beverage cartons, paper and cardboard) together in the same bin/bag. 

Recyclables must still be kept separate from trash at all times. 

Private carters that are authorized to collect single-stream recycling can collect recyclables in one truck-- separate from trash. Carters must deliver the materials directly to a recycling facility capable of receiving, separating and processing commingled recyclables.

Businesses utilizing single-stream recycling are required to post an official BIC decal indicating that single-stream is used and include the name and license number of the private carter that is authorized to collect single-stream recyclables.""",

"storing_containers": """ Bins should be stored inside or in a rear yard if possible. If space is not available, bins can be stored within 3 feet of the building line when not set out for collection. 

Bins placed on the sidewalk must be maintained in a neat and orderly manner and allow a clear path for pedestrians.

It is illegal to chain bins to public property.

Exceptions

This requirement does not apply to:

Recyclables (metal, glass, plastic, or paper) 
Businesses that have waste collected from a loading dock
""",

"recycling_rules": """Businesses are required to recycle certain materials and make sure, as much as possible, that the items are properly handled by their private carter.  

Businesses must also post easily visible recycling signs and provide clearly labeled recycling containers, so that both employees and customers know what and where to recycle. 

Businesses are required to recycle: 

Metal (all kinds) 

Metal cans (including soup and food cans, empty aerosol cans, dried-out paint cans) 
Aluminum foil and foil products (wrap and trays) 
Metal caps and lids 
Industry-specific metal (such as wire hangers, pots, tools, curtain rods, small appliances that are mostly metal, etc.) 
Large or bulky metal items (furniture and cabinets; large appliances such as microwaves, washing machines, refrigerators, etc.) 
Glass 

Glass bottles 
Glass jars 
Plastic (all rigid plastics) 

Plastic bottles, jugs, and jars 
Rigid plastic caps and lids 
Rigid plastic food containers (such as yogurt, deli,” clamshell” containers and other plastic take-out containers) 
Rigid plastic non-food containers 
Rigid plastic packaging (such as "blister-pack" and "clamshell" consumer packaging, acetate boxes) 
Rigid plastic wares (such as flowerpots, mixing bowls, and plastic appliances) 
Bulk rigid plastic (like crates, buckets, pails, and furniture) 
Please note: rigid plastic is any item that is mostly plastic resin—it is relatively inflexible and maintains its shape or form when bent. 

Beverage Cartons 

Milk or juice cartons 
Drink boxes 
Aseptic packaging (holds beverages and food: juice, non-refrigerated milk, soup, etc.) 
Paper 

Newspapers, magazines, catalogs 
White and colored paper (including lined, copier, and computer paper; staples are ok) 
Mail and envelopes (any color; window envelopes are ok) 
Receipts 
Paper bags (handles ok)  
Wrapping paper 
Soft-cover books (such as paperbacks and comics; no spiral bindings) 
Cardboard 

Smooth cardboard (such as food and shoe boxes, tubes, file folders, and cardboard from product packaging) 
Cardboard egg cartons and trays 
Pizza boxes (remove and discard soiled liner) 
Corrugated cardboard boxes """,
    
   "bottle_and_can_deposit_fees": """ New York's Returnable Container Act requires retailers to collect a deposit on every eligible container they sell, and to accept returns of containers for deposit refunds.

Retailers and distributors of beverages in containers for off-premises consumption in NY State must:

Collect a 5¢ deposit on the sale of each container
Accept covered types of containers for recycling
Pay refunds during normal business hours
Local law requires that beverage dealers in New York City prominently post a sign or signs summarizing the rights and obligations of redeemers under the New York State Environmental Conservation Law.

Businesses can refuse to return a deposit if:

Your store doesn't carry that type of container
The container doesn't have a proper New York refund label
The container has anything in it besides a small amount of dirt, dust or moisture
Bottles are broken or cans are corroded or crushed """,

"textiles": """ f textiles make up more than 10% of your business’s waste during any month, you are required by law to separate and recycle or repurpose all textile waste, including fabric scraps, clothing, belts, bags, and shoes
 You can get more information via this website url: https://www.nyc.gov/site/dsny/businesses/materials-handling/textiles.page""",

"separating_textiles": """If textiles make up more than 10% of your business's waste during any month, you are required by law to separate and recycle or repurpose all textile waste, including:

Fabric scraps
Clothing
Hats
Belts
Bags
Shoes
Clean rags
Bedding
Towels
Curtains
""", 

"textile_recycling_and_resuse": """ donateNYC
By donating and reusing goods instead of discarding them, New Yorkers can greatly reduce waste, conserve energy and resources, save money, and help provide jobs and human services for New Yorkers in need.

Businesses and nonprofit organizations can use the donateNYC Exchange, an online materials reuse platform, to give or receive gently used and surplus materials.

DSNY Textile Recycling Collection Service
We offer a free, in-building collection program for clothing and other fabric items for NYC residents, businesses, schools, and nonprofits.

Office buildings and businesses such as fashion and apparel, storage facilities, gyms, laundromats, and hotels are eligible. Receipts for tax deductions are available for donations.

You can get more information via this website url: https://www.nyc.gov/site/dsny/what-we-do/programs/textile-collection.page

""",
 "enroll_in_textile_recycling": """ To enroll in the DSNY Textile Recycling Collection Service, please complete and submit the Textile Recycling Collection Service Enrollment Form. A DSNY representative will contact you to schedule your first collection.
 
 Enroll your building in our free textile recycling collection service.

This service is available for:

Apartment buildings with 10 or more units
Office buildings
Commercial industries (fashion and apparel businesses, storage facilities, gyms, laundromats, hotels)
Schools, City agencies, and nonprofits

This is the website url to enroll: https://www.nyc.gov/assets/dsny/forms/refashion-nyc""",

"yard_and_plant_waste": """ If yard or plant waste makes up more than 10% of your business’s waste during any month, you are required by law to separate out organic waste and dispose of it separate from trash or recycling. This including grass clippings, garden debris, leaves, and branches. """,

"commerical_landscapers": """ Commercial landscapers MUST dispose of ALL their leaf and yard waste at permitted composting facilities. Plant waste generated by landscaping professionals CANNOT be set out for curbside collection or dispersed in or around streets, curbs, or neighboring lots.

Staten Island Compost Facility
The City's largest permitted compost facility is DSNY's Staten Island Compost Facility (SICF).

The facility accepts yard and plant waste from commercial landscapers, NYC agencies, and nonprofits. Additionally, it processes food scraps and yard waste from residential composting collection.

NOTE: Yard and plant waste drop-off is for businesses and nonprofits ONLY. We DO NOT accept food scrap and yard waste drop-offs from residents. Residents should use Curbside Composting collection or find at Smart Compost bin or community drop-off site.

Location and Hours
450 West Service Road
Staten Island, NY 10313
Phone: (917) 830-0076

Facility entrance at 600 West Service Road
(Route 440 South, Exit 7, Victory Boulevard)

Open Monday through Saturday, 7:00 AM to 3:00 PM.

The facility is closed on major holidays.

Opening an Account
Landscaping and tree service companies must open an account with DSNY to dispose of plant waste and purchase compost at the Staten Island Compost Facility. Companies seeking permits must already have valid licenses from the Business Integrity Commission.

You will need to fill out an application in person to open an account. One account can include multiple vehicles, but EACH vehicle must be inspected and measured by DSNY and registered separately.

To open a new account or add a new vehicle to an existing account, call the facility at (917) 830-0076 to set up an appointment.

Nonprofits and NYC agencies must also go through a registration process in order to use the Staten Island Compost Facility.

Materials Accepted
The facility accepts leaves, brush, grass clippings, Christmas trees, wood chips, stumps, and logs. Trees, stumps and logs must be less than 32 inches in diameter and 6 feet in length.

NOTE: Loads containing any other materials will be rejected. If your load is rejected, you will be required to remove the material and you will not receive a refund.

Procedures and Costs
Every time you deliver yard waste for disposal or purchase compost or mulch, you must present your vehicle-specific permit to the scale attendant.

Only major credit cards and debit cards are accepted. NO REFUNDS.

Disposal
The cost to dispose of plant waste is $12 per cubic yard. You will be charged for your vehicle's full registered capacity, regardless of the quantity of material in the vehicle.

EXAMPLE: If your permit says your truck has an 8 cubic-yard capacity, you will be charged $96 to discard the plant waste in your truck.
Purchasing
The cost to purchase compost and mulch is $14 per cubic yard.

You can get more information via this website url: https://www.nyc.gov/site/dsny/businesses/setup-operations/commercial-landscapers.page""",

"electronic_rules": """ Some electronics contain hazardous materials, including lead, mercury, arsenic, and cadmium. You can’t dispose of these electronics, also called e-waste, with your regular trash or recycling.

E-waste includes:

Computers and Computer Accessories

Desktop towers, monitors, laptops, and tablets (ex: iPads)
Keyboards, mice, and pointing devices
Printers and document scanners
Cables, cords, and wiring permanently fixed to a device
Small-scale servers
TV and Video Equipment

TVs, VCRs, DVD players, DVRs (digital video recorders)
Cable boxes, cable/satellite receivers, antennas, digital converter boxes
Cables, cords, and wiring permanently fixed to the TV
Portable Electronic Devices

Laptops, tablets (iPads), and e-readers
Portable music devices/digital music players (iPod, mp3 player, Walkman)
Digital cameras
Cell phones
Home Electronics

Video game consoles
Fax machines
Electronic keyboards
Small businesses with fewer than 50 full-time employees, and nonprofits with fewer than 75 employees, are eligible for free and convenient electronics recycling provided by manufacturers. Contact the product manufacturer for more information. You can get a list of registered electronic equipment manufacturers.

Large businesses should first consider donating their unwanted electronics to a charitable organization or school. If donating is not an option, businesses must contract with an electronic waste recycler. When choosing a recycler, look for e-stewards or R2 certification to help ensure that your electronics are recycled responsibly. The NY State Department of Environmental Conservation maintains a list of registered recyclers.

Non-Hazardous E-Waste Removal

E-waste that is not classified as hazardous waste per the NY State Department of Environmental Conservation can be collected by a private carter or you can register as a self-hauler to remove it yourself.""",

"regulated_medical_waste": """New York State's Regulated Medical Waste Program regulates the handling, storage, treatment, and disposal of certain waste produced by hospitals, diagnostic and treatment centers, residential health care facilities, and clinical laboratories. It is jointly administered by NY State Department of Health (DOH) and the Department of Environmental Conservation (DEC).

Regulated medical waste includes:

Human blood and blood products
Needles and syringes (sharps)
Laboratory waste (cultures, microbiological materials, dyalysus waste)
Human pathological waste
Contaminated or infectious animal carcasses
Material contaminated with blood, body fluids, or other infectious waste
Waste from surgery or autopsies
Medical waste disposal regulations apply to:

Hospitals
Health care facilities
Nursing homes
Diagnostic and treatment facilities
Clinical and research laboratories
Veterinary clinics
Pharmacies
Funeral homes
Regulated institutions with medical waste must file reports to the NYS Department of Environmental Conservation.

An annual Solid Waste Removal Plan must be subimtted to DSNY.

""",

"sharps": """New York State law requires hospitals and nursing homes to help New Yorkers safely dispose of needles, syringes, lancets, and other sharp objects.

Pharmacies are not required to participate in sharps take-backs, but may choose to participate in the Expanded Syringe Access Program (ESAP).

Learn more about the NYS Safe Sharps Collection Program.""", 

"NYS_Safe_Sharps_Collection_Program": """ There are many individuals with serious health conditions who manage their care at home and use syringes. For example, people with diabetes use syringes to inject their own insulin and use lancets every day to test their blood glucose. In addition, people who use drugs also need to dispose of used syringes and needles.

Safe disposal of sharps is critically important to optimize health, safety and protection of the environment and the community. The best way to ensure that people are protected from potential injury or disease transmission of blood borne diseases due to needle sticks is to follow established guidelines for the proper containment of “sharps” syringes, needles and lancets and other safer disposal practices.

Three methods of disposing syringes and other sharps collection sites exist across New York State.

All hospitals and nursing homes in New York State are mandated by law to accept home-generated sharps as a free, community service through their sharps collection programs.

Locate a hospital in your region. Go to NYS Health Profiles to search by region or county.
Locate a nursing home in your region. Go to NYS Health Profiles to search by region or county.
Call first: Ask to speak with the facility's sharps coordinator for hours of operation, directions, drop-off sites, etc.
Nursing home not accepting household sharps? Nursing Home Complaint Form
For more information, call the facility's main phone number and ask to be connected to their Sharps Coordinator.
In addition, pharmacies, health clinics, community-based organizations, mobile van programs, public transportation facilities, housing projects, police stations, waste transfer stations and other venues have become settings for safe sharps and offer syringe collection drop boxes (or "kiosks") to help facilitate the safe collection of used sharps.

These facilities and alternative sites are listed in the directory below:

Know Your Local Recycling Guidelines
Locate Expanded Syringe Access Program disposal sites: AIDS Institute Provider Directory
Service providers may share the above directories to educate clients and to refer them to convenient places in the community where they can safely dispose of their household sharps.

Although every attempt has been made to keep the directories updated, service information may have changed since data was collected. Before visiting the location, we suggest calling the phone number a long-side the site you are interested in to confirm program information. Information posted on this website will be updated regularly as new information becomes available.

Facilities wishing to update information about their community sharps collection sites should e-mail their updated information to: ESAP@health.ny.gov  """,

"plastic_straws_splash_sticks_and_stirrers": """ As of November 1, 2021, New York City food service businesses may no longer provide single-use plastic beverage straws, except upon request.

Additionally, food service businesses may no longer provide single-use beverage splash sticks or stirrers made of plastic.

Learn more about Local Law 64 of 2021. Call 311 to submit complaints or questions.

Businesses May Provide:

Beverage straws that are compostable and not made of plastic (ex. compostable paper)
Beverage splash sticks and stirrers that are compostable and not made of plastic (ex. wood)
Upon Request Only:

All food service businesses must maintain a sufficient supply of single-use plastic beverage straws that are not compostable and provide these, free of charge, to any person who requests one. Not doing so may violate the reasonable accommodations provisions of Title 8 of the Administrative Code of New York City. This is subject to enforcement by the NYC Commission on Human Rights.
Businesses that are covered by the Commercial Organics Rules may provide straws made of compostable plastics upon request only if such straws are used on premises and they are source separated from trash and other recyclables to be collected by a Business Integrity Commission (BIC) licensed organics carter.
Food service businesses with self-serve stations must display a sign at each station that states: "Plastic Straws Available Upon Request."
These signs must be:

Highly visible and unobstructed
At least two inches by seven inches
Use at least a 20-point font size
Download a sample sign.

Exemptions
These restrictions do not apply to items that are packaged in bulk by a manufacturer and offered for retail sale or beverage straws attached to individual containers by the manufacturer, such as juice boxes.

Enforcement
These restrictions went into effect on November 1, 2021. There was a one-year warning period that ended on October 31, 2022.

Affected businesses, agencies, and nonprofits should be prepared to receive inspectors, at least annually as part of routine inspections or 311 investigations, from one or more of the following agencies:

NYC Department of Sanitation
NYC Department of Health and Mental Hygiene
NYC Department of Consumer and Worker Protection
Failure to comply with Local Law 64 of 2021 may result in a Notice of Violation and civil action may be taken.

Alternatives
There are many options available including compostable paper and wood products. Contact your distributor about alternatives to single-use plastic beverage straws, splash sticks, and stirrers.

Additional Resources
We provide educational materials to educate your staff and customers on the law and help businesses transition away from single-use plastics. """, 

"Single_use_plastic_bags": """ Single-use plastic carryout bags are banned, with limited exceptions, in New York State. as of October 19, 2020. Learn more about the New York State Department of Environmental Conservation's Bag Waste Reduction Act.

Prior to this law, NYC residents used more than 10 billion single-use carryout bags every year — costing our City more than $12 million annually to dispose of these bags.

New York State created a task force that analyzed the impacts of single-use plastic bags and issued a report: Learn more about the task force and read the report.

Compliance
Any retailer that is required to collect New York State sales tax (with limited exceptions) will no longer be able to provide single-use plastic carryout bags. Learn more about the exceptions to the ban and how to comply.
 
Additionally, all NYC businesses covered by the ban must charge a five-cent ($0.05) fee on paper bags. Learn more about the carryout bag reduction fee and how to comply.

NOTE: This fee does not apply to any customers using SNAP or WIC.

Business Take-Back Program Requirement
The New York State's Plastic Bag Reduction, Reuse and Recycling Act has been in effect since January 1, 2009.

Large retailers are required to take back all types of film plastic for recycling, including single-use plastic carryout bags from residents.

Visit the New York State Department of Environmental Conservation for more information.""",

    }
}
    
    