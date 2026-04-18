
#!/usr/bin/env python3
"""
Generate synthetic but realistic municipal seed data for the Municipal Licensing & Property Platform.

Outputs:
- current-schema API payloads
- richer v2 CSV model for future UI/UX expansion
- dashboard KPI references
- sample text attachments
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import statistics
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

MALE_FIRST = ["Aarav","Aditya","Akash","Amit","Aniket","Anil","Arjun","Ashish","Atul","Chetan","Deepak","Ganesh","Harshal","Kailas","Mahesh","Milind","Nikhil","Omkar","Prakash","Rajesh","Rohit","Sachin","Sagar","Sameer","Sandeep","Shailesh","Shubham","Siddharth","Sunil","Swapnil","Umesh","Vijay","Vikas","Yogesh"]
FEMALE_FIRST = ["Aarti","Anagha","Anita","Asha","Deepa","Dipali","Gayatri","Kavita","Komal","Madhuri","Manisha","Meera","Neha","Pooja","Prajakta","Priya","Rashmi","Rutuja","Savita","Shalini","Sheetal","Shraddha","Sneha","Sonali","Sunita","Supriya","Swati","Vaishali","Varsha","Vidya"]
SURNAMES = ["Agarwal","Bansode","Chavan","Deshmukh","Gadgil","Gaikwad","Jadhav","Joshi","Kadam","Kale","Kapoor","Karnik","Khan","Khot","Kulkarni","Mahajan","Mehta","More","Naik","Patel","Patil","Pawar","Raut","Shah","Shinde","Singh","Sutar","Thorve","Wagh","Yadav"]
BUSINESS_PREFIX = ["Sai","Shree","Om","Mahalaxmi","A1","Supreme","Skyline","Sunrise","Greenfield","Galaxy","Siddhi","Global","Metro","Vardhaman","Silver","Pratham","Nirman","Urban","Reliable","Fortune"]
BUSINESS_SUFFIX = ["Traders","Foods","Enterprises","Developers","Associates","Stores","Pharmacy","Bakery","Mart","Solutions","Engineering","Warehousing","Hospitality","Lounge","Stationers","Logistics","Decor","Industries","Agency","Builders"]
ROAD_NAMES = ["Main Road","Link Road","Internal Road","Market Road","Station Road","Temple Road","Service Road","Garden Road","Cross Lane","Old Village Road","Junction Road","Mahatma Phule Road","Tilak Path","MG Road","DP Road","Canal Road","Ring Road"]

PROPERTY_STATUS_WEIGHTS = [("active", 0.88), ("under_verification", 0.05), ("disputed", 0.03), ("sealed", 0.02), ("inactive", 0.02)]
USE_TYPE_WEIGHTS = [("residential", 0.46), ("commercial", 0.24), ("mixed_use", 0.16), ("institutional", 0.07), ("industrial", 0.04), ("vacant_land", 0.03)]
LICENSE_STATUS_WEIGHTS = [("draft", 0.12), ("submitted", 0.24), ("under_review", 0.28), ("approved", 0.28), ("rejected", 0.08)]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def weighted_choice(weighted_items):
    labels, weights = zip(*weighted_items)
    return random.choices(labels, weights=weights, k=1)[0]


def random_name() -> str:
    return f"{random.choice(MALE_FIRST + FEMALE_FIRST)} {random.choice(SURNAMES)}"


def business_name() -> str:
    return f"{random.choice(BUSINESS_PREFIX)} {random.choice(BUSINESS_SUFFIX)}"


def synthetic_mobile(seq: int) -> str:
    return f"9{seq:09d}"[-10:]


def jitter(center, radius_lat=0.012, radius_lng=0.012):
    lat, lng = center
    return round(lat + random.uniform(-radius_lat, radius_lat), 6), round(lng + random.uniform(-radius_lng, radius_lng), 6)


def area_for_use(use_type: str):
    if use_type == "residential":
        land = random.randint(40, 500)
        bua = round(land * random.uniform(0.9, 3.0), 1)
    elif use_type == "commercial":
        land = random.randint(35, 1200)
        bua = round(land * random.uniform(1.2, 4.5), 1)
    elif use_type == "mixed_use":
        land = random.randint(50, 900)
        bua = round(land * random.uniform(1.0, 3.5), 1)
    elif use_type == "institutional":
        land = random.randint(300, 4000)
        bua = round(land * random.uniform(0.8, 2.2), 1)
    elif use_type == "industrial":
        land = random.randint(150, 5000)
        bua = round(land * random.uniform(0.7, 2.5), 1)
    else:
        land = random.randint(80, 3000)
        bua = round(land * random.uniform(0.0, 0.3), 1)
    return land, bua


def rateable_value(city: str, use_type: str, bua: float) -> int:
    base = {
        "Pune": {"residential": 110, "commercial": 260, "mixed_use": 190, "institutional": 95, "industrial": 160, "vacant_land": 20},
        "Mumbai": {"residential": 280, "commercial": 620, "mixed_use": 470, "institutional": 170, "industrial": 350, "vacant_land": 55},
    }
    return int(max(12000, bua * base[city][use_type] * random.uniform(0.9, 1.35)))


def estimated_property_tax(city: str, use_type: str, bua: float) -> int:
    base_rate = {
        "Pune": {"residential": 24, "commercial": 52, "mixed_use": 38, "institutional": 18, "industrial": 34, "vacant_land": 6},
        "Mumbai": {"residential": 65, "commercial": 150, "mixed_use": 102, "institutional": 42, "industrial": 88, "vacant_land": 18},
    }
    return int(max(2500, bua * base_rate[city][use_type] * random.uniform(0.8, 1.25)))


def probable_license_types_for_use(use_type: str):
    if use_type == "commercial":
        return [("trade_license", 0.42), ("signboard_permission", 0.14), ("health_noc", 0.14), ("fire_referral", 0.10), ("building_plan_approval", 0.08), ("occupancy_certificate", 0.08), ("storage_noc", 0.04)]
    if use_type == "mixed_use":
        return [("trade_license", 0.30), ("signboard_permission", 0.10), ("building_plan_approval", 0.20), ("occupancy_certificate", 0.16), ("health_noc", 0.08), ("fire_referral", 0.08), ("storage_noc", 0.08)]
    if use_type == "institutional":
        return [("fire_referral", 0.20), ("occupancy_certificate", 0.22), ("building_plan_approval", 0.24), ("health_noc", 0.16), ("trade_license", 0.10), ("storage_noc", 0.08)]
    if use_type == "industrial":
        return [("storage_noc", 0.22), ("fire_referral", 0.20), ("building_plan_approval", 0.20), ("occupancy_certificate", 0.14), ("trade_license", 0.16), ("health_noc", 0.08)]
    if use_type == "vacant_land":
        return [("building_plan_approval", 0.55), ("occupancy_certificate", 0.05), ("estate_permission", 0.20), ("trade_license", 0.10), ("signboard_permission", 0.10)]
    return [("building_plan_approval", 0.18), ("occupancy_certificate", 0.14), ("trade_license", 0.20), ("health_noc", 0.10), ("signboard_permission", 0.10), ("fire_referral", 0.12), ("estate_permission", 0.06), ("storage_noc", 0.10)]


def fee_for_license(city_name: str, license_type: str, use_type: str, bua: float) -> int:
    base = {
        "trade_license": 3500,
        "health_noc": 4200,
        "signboard_permission": 5000,
        "building_plan_approval": 25000,
        "occupancy_certificate": 15000,
        "storage_noc": 6000,
        "estate_permission": 8000,
        "fire_referral": 4500,
    }[license_type]
    city_factor = 1.0 if city_name == "Pune" else 1.45
    use_factor = {
        "residential": 0.8,
        "commercial": 1.2,
        "mixed_use": 1.1,
        "institutional": 1.0,
        "industrial": 1.35,
        "vacant_land": 0.75,
    }[use_type]
    area_factor = max(1.0, min(6.0, bua / 120))
    if license_type not in {"building_plan_approval", "occupancy_certificate"}:
        area_factor = max(1.0, min(3.0, bua / 200))
    amount = int(base * city_factor * use_factor * area_factor * random.uniform(0.85, 1.20))
    return int(round(amount / 100.0) * 100)


def write_json(path: Path, obj: dict | list):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict], fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        ordered = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    ordered.append(key)
                    seen.add(key)
        fieldnames = ordered
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_users(pune_wards: list[dict], mumbai_wards: list[dict]) -> list[dict]:
    users: list[dict] = []
    for city_prefix, wards in [("pmc", pune_wards), ("bmc", mumbai_wards)]:
        users.append({
            "subject": f"{city_prefix}-admin-01",
            "username": f"{city_prefix}.admin",
            "email": f"{city_prefix}.admin@municipal.local",
            "department": "Municipal Administration",
            "active": True,
            "roles": ["municipal-admin"],
        })
        for i, ward in enumerate(wards, start=1):
            short_name = re.sub(r"[^a-z0-9]+", "", ward["ward_name"].lower())[:14]
            username = f"{city_prefix}.lic.{short_name}"
            users.append({
                "subject": f"{city_prefix}-lic-{i:02d}",
                "username": username,
                "email": f"{username}@municipal.local",
                "department": f"License Department - {ward['ward_name']}",
                "active": True,
                "roles": ["licensing-officer"],
            })
        for j in range(1, 4):
            users.append({
                "subject": f"{city_prefix}-viewer-{j:02d}",
                "username": f"{city_prefix}.viewer{j}",
                "email": f"{city_prefix}.viewer{j}@municipal.local",
                "department": "Citizen Facilitation Centre",
                "active": True,
                "roles": ["viewer"],
            })
        users.append({
            "subject": f"{city_prefix}-audit-01",
            "username": f"{city_prefix}.audit",
            "email": f"{city_prefix}.audit@municipal.local",
            "department": "Internal Audit",
            "active": True,
            "roles": ["auditor"],
        })
    return users


def choose_ward(city_name: str, pune_wards: list[dict], mumbai_wards: list[dict]) -> dict:
    wards = pune_wards if city_name == "Pune" else mumbai_wards
    return random.choices(wards, weights=[w["weight"] for w in wards], k=1)[0]


def make_property_number(city_name: str, ward: dict, serial: int) -> str:
    city_prefix = "PMC" if city_name == "Pune" else "BMC"
    return f"{city_prefix}-{ward['ward_code'].split('-')[-1]}-{random.choice(ward['postal_codes'])}-{serial:06d}"


def make_property_address(ward: dict):
    area = random.choice(ward["areas"])
    plot = random.randint(1, 999)
    cts = random.randint(10, 9999)
    final_plot = random.randint(1, 250)
    road = random.choice(ROAD_NAMES)
    building = random.choice(["Sadan", "Heights", "Plaza", "Arcade", "Annex", "Bhavan", "Complex", "Residency", "Enclave", "Court"])
    line1 = f"CTS {cts}, Final Plot {final_plot}, {area} {road}"
    line2 = f"{random.randint(1,20)}-{building}, Near {ward['ward_name']} Office"
    return line1, line2, plot, cts, final_plot, area


def estimate_assessment_zone(city_name: str, ward: dict) -> str:
    if city_name == "Pune":
        return random.choice([ward["zone"], f"{ward['zone']} Core", f"{ward['zone']} Extension"])
    return random.choice([ward["zone"], f"{ward['zone']} A", f"{ward['zone']} B"])


def build_profile(profile_name: str, profile_cfg: dict, catalog: dict, users: list[dict], seed: int):
    random.seed(seed)
    pune_wards = catalog["pune_wards"]
    mumbai_wards = catalog["mumbai_wards"]
    property_count = profile_cfg["property_count"]
    license_ratio = profile_cfg["license_ratio"]

    city_mix = {
        "developer_seed": {"Pune": 0.50, "Mumbai": 0.50},
        "pune_demo": {"Pune": 1.0},
        "mumbai_demo": {"Mumbai": 1.0},
        "hybrid_demo": {"Pune": 0.46, "Mumbai": 0.54},
        "load_medium": {"Pune": 0.45, "Mumbai": 0.55},
    }.get(profile_name, {"Pune": 0.5, "Mumbai": 0.5})

    properties = []
    properties_v2 = []
    city_serial = defaultdict(int)

    for index in range(1, property_count + 1):
        city_name = random.choices(list(city_mix.keys()), weights=list(city_mix.values()), k=1)[0]
        ward = choose_ward(city_name, pune_wards, mumbai_wards)
        city_serial[(city_name, ward["ward_code"])] += 1
        serial = city_serial[(city_name, ward["ward_code"])]
        use_type = weighted_choice(USE_TYPE_WEIGHTS)
        status = weighted_choice(PROPERTY_STATUS_WEIGHTS)
        land_area, built_up_area = area_for_use(use_type)
        property_number = make_property_number(city_name, ward, serial)
        line1, line2, plot_no, cts_no, final_plot_no, area_name = make_property_address(ward)
        lat, lng = jitter(ward["center"], 0.01 if city_name == "Pune" else 0.014, 0.01 if city_name == "Pune" else 0.014)
        owner_name = random_name() if random.random() < 0.72 else business_name()
        owner_contact = synthetic_mobile(index)
        prop_id = str(uuid.uuid4())
        created_at = datetime(2025, 10, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 190), minutes=random.randint(0, 1440))
        updated_at = created_at + timedelta(days=random.randint(0, 120), minutes=random.randint(0, 1440))
        remarks = (
            f"Area context: {area_name}. Approx. land {land_area} sq m, built-up {built_up_area} sq m. "
            f"Synthetic record for realistic municipal testing only."
        )
        properties.append({
            "id": prop_id,
            "property_number": property_number,
            "ward_code": ward["ward_code"],
            "address_line_1": line1,
            "address_line_2": line2,
            "city": ward["city"],
            "district": ward["district"],
            "state": ward["state"],
            "postal_code": random.choice(ward["postal_codes"]),
            "geo_lat": lat,
            "geo_lng": lng,
            "status": status,
            "use_type": use_type,
            "owner_name": owner_name,
            "owner_contact": owner_contact,
            "assessment_zone": estimate_assessment_zone(city_name, ward),
            "remarks": remarks,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "ward_name": ward["ward_name"],
            "zone_name": ward["zone"],
            "area_name": area_name,
        })
        properties_v2.append({
            "property_id": prop_id,
            "property_number": property_number,
            "city": ward["city"],
            "ward_code": ward["ward_code"],
            "ward_name": ward["ward_name"],
            "zone_name": ward["zone"],
            "area_name": area_name,
            "plot_no": plot_no,
            "survey_no": random.randint(1, 300),
            "cts_no": cts_no,
            "final_plot_no": final_plot_no,
            "postal_code": random.choice(ward["postal_codes"]),
            "geo_lat": lat,
            "geo_lng": lng,
            "land_area_sq_m": land_area,
            "built_up_area_sq_m": built_up_area,
            "occupancy_type": random.choices(["owner_occupied", "rented", "mixed"], weights=[0.52, 0.31, 0.17], k=1)[0],
            "annual_rateable_value_inr": rateable_value(city_name, use_type, built_up_area),
            "estimated_property_tax_inr": estimated_property_tax(city_name, use_type, built_up_area),
            "status": status,
            "use_type": use_type,
            "owner_name": owner_name,
            "owner_contact": owner_contact,
            "structural_risk_band": random.choices(["low", "medium", "high"], weights=[0.72, 0.23, 0.05], k=1)[0],
            "last_field_verification_date": (updated_at - timedelta(days=random.randint(0, 90))).date().isoformat(),
            "remarks": remarks,
        })

    property_map = {p["id"]: p for p in properties}
    property_v2_map = {p["property_id"]: p for p in properties_v2}

    def officer_for_property(prop: dict) -> dict:
        city_prefix = "pmc" if prop["city"] == "Pune" else "bmc"
        short_name = re.sub(r"[^a-z0-9]+", "", prop["ward_name"].lower())[:14]
        target = f"{city_prefix}.lic.{short_name}"
        for user in users:
            if user["username"] == target:
                return user
        for user in users:
            if user["subject"].startswith(f"{city_prefix}-lic-"):
                return user
        return users[0]

    def applicant_for_property(prop: dict) -> str:
        if prop["use_type"] in {"commercial", "mixed_use", "industrial"} and random.random() < 0.45:
            return business_name()
        return random_name()

    def app_number(city_name: str, license_type: str, serial: int) -> str:
        city_prefix = "PMC" if city_name == "Pune" else "BMC"
        code = {
            "trade_license": "TRD",
            "health_noc": "HLT",
            "signboard_permission": "SBD",
            "building_plan_approval": "BPA",
            "occupancy_certificate": "OCC",
            "storage_noc": "STO",
            "estate_permission": "EST",
            "fire_referral": "FIR",
        }[license_type]
        return f"{city_prefix}-{code}-2026-{serial:06d}"

    licenses = []
    licenses_v2 = []
    workflow_events = []
    audit_events = []
    documents = []

    eligible = [p for p in properties if p["status"] not in {"inactive", "sealed"}]
    license_count = int(round(len(properties) * license_ratio))
    chosen_props = random.sample(eligible, min(len(eligible), license_count))
    created_base = datetime(2025, 11, 1, tzinfo=timezone.utc)

    for serial, prop in enumerate(chosen_props, start=1):
        license_type = weighted_choice(probable_license_types_for_use(prop["use_type"]))
        status = weighted_choice(LICENSE_STATUS_WEIGHTS)
        officer = officer_for_property(prop)
        applicant_name = applicant_for_property(prop)
        applicant_contact = synthetic_mobile(800000000 + serial)
        application_number = app_number(prop["city"], license_type, serial)
        created_at = created_base + timedelta(days=random.randint(0, 150), minutes=random.randint(0, 1440))
        submitted_at = None
        decided_at = None
        review_time = None
        current_assignee = None
        actions = []

        if status in {"submitted", "under_review", "approved", "rejected"}:
            submitted_at = created_at + timedelta(hours=random.randint(1, 72))
            actions.append(("submit", "draft", "submitted", applicant_name.lower().replace(" ", ".")[:24]))
        if status in {"under_review", "approved", "rejected"}:
            review_time = submitted_at + timedelta(days=random.randint(1, 6), hours=random.randint(0, 8))
            actions.append(("review", "submitted", "under_review", officer["subject"]))
            current_assignee = officer["username"]
        if status == "approved":
            decided_at = review_time + timedelta(days=random.randint(1, 10), hours=random.randint(0, 8))
            actions.append(("approve", "under_review", "approved", officer["subject"]))
        elif status == "rejected":
            decided_at = review_time + timedelta(days=random.randint(1, 8), hours=random.randint(0, 8))
            actions.append(("reject", "under_review", "rejected", officer["subject"]))

        note = (
            f"{license_type.replace('_', ' ').title()} workflow for {prop['ward_name']}."
            f" Target state is {status}. Synthetic demo record."
        )

        license_id = str(uuid.uuid4())
        licenses.append({
            "id": license_id,
            "application_number": application_number,
            "property_id": prop["id"],
            "license_type": license_type,
            "status": status,
            "applicant_name": applicant_name,
            "applicant_contact": applicant_contact,
            "current_assignee": current_assignee,
            "submitted_at": submitted_at.isoformat() if submitted_at else "",
            "decided_at": decided_at.isoformat() if decided_at else "",
            "notes": note,
            "created_at": created_at.isoformat(),
            "updated_at": (decided_at or submitted_at or created_at).isoformat(),
            "property_number": prop["property_number"],
            "ward_code": prop["ward_code"],
            "ward_name": prop["ward_name"],
            "city": prop["city"],
            "transition_path": [a[0] for a in actions],
            "assignee_subject": officer["subject"],
            "assignee_username": officer["username"],
        })

        built_up_area = property_v2_map[prop["id"]]["built_up_area_sq_m"]
        licenses_v2.append({
            "license_id": license_id,
            "application_number": application_number,
            "property_id": prop["id"],
            "property_number": prop["property_number"],
            "city": prop["city"],
            "ward_code": prop["ward_code"],
            "ward_name": prop["ward_name"],
            "license_type": license_type,
            "application_stage": status,
            "filing_channel": random.choices(["web_portal", "counter_entry", "architect_portal", "department_intake"], weights=[0.42, 0.18, 0.28, 0.12], k=1)[0],
            "applicant_name": applicant_name,
            "applicant_contact": applicant_contact,
            "assigned_department": officer["department"],
            "current_assignee": officer["username"] if current_assignee else "",
            "sla_days": {
                "trade_license": 10,
                "health_noc": 12,
                "signboard_permission": 7,
                "building_plan_approval": 30,
                "occupancy_certificate": 21,
                "storage_noc": 14,
                "estate_permission": 18,
                "fire_referral": 10,
            }[license_type],
            "fee_amount_inr": fee_for_license(prop["city"], license_type, prop["use_type"], built_up_area),
            "payment_status": random.choices(["pending", "paid", "waived"], weights=[0.19, 0.77, 0.04], k=1)[0],
            "requires_site_inspection": random.choices([True, False], weights=[0.58, 0.42], k=1)[0],
            "risk_band": random.choices(["low", "medium", "high"], weights=[0.6, 0.28, 0.12], k=1)[0],
            "created_at": created_at.isoformat(),
            "submitted_at": submitted_at.isoformat() if submitted_at else "",
            "decided_at": decided_at.isoformat() if decided_at else "",
            "remarks": note,
        })

        workflow_events.append({
            "id": str(uuid.uuid4()),
            "aggregate_type": "license",
            "aggregate_id": license_id,
            "action": "create",
            "from_state": "",
            "to_state": "draft",
            "actor_subject": officer["subject"] if random.random() < 0.4 else applicant_name.lower().replace(" ", ".")[:24],
            "comments": "Application created",
            "license_id": license_id,
            "created_at": created_at.isoformat(),
        })
        for action, from_state, to_state, actor_subject in actions:
            event_time = submitted_at if action == "submit" else review_time if action == "review" else decided_at
            workflow_events.append({
                "id": str(uuid.uuid4()),
                "aggregate_type": "license",
                "aggregate_id": license_id,
                "action": action,
                "from_state": from_state,
                "to_state": to_state,
                "actor_subject": actor_subject,
                "comments": note,
                "license_id": license_id,
                "created_at": event_time.isoformat(),
            })

        audit_events.append({
            "id": str(uuid.uuid4()),
            "event_type": "license.created",
            "subject": license_id,
            "actor": officer["subject"],
            "outcome": "success",
            "ip_address": f"10.20.{random.randint(1,200)}.{random.randint(1,250)}",
            "detail_message": f"Created license application {application_number}",
            "details_json": json.dumps({"ward_code": prop["ward_code"], "city": prop["city"], "license_type": license_type}),
            "created_at": created_at.isoformat(),
        })

        if status in {"approved", "rejected"}:
            audit_events.append({
                "id": str(uuid.uuid4()),
                "event_type": f"license.{status}",
                "subject": license_id,
                "actor": officer["subject"],
                "outcome": "success",
                "ip_address": f"10.20.{random.randint(1,200)}.{random.randint(1,250)}",
                "detail_message": f"{status.title()} license application {application_number}",
                "details_json": json.dumps({"decision_state": status}),
                "created_at": decided_at.isoformat(),
            })

        doc_count = random.randint(1, 4 if license_type in {"building_plan_approval", "occupancy_certificate"} else 3)
        categories = ["application_note", "ownership_note", "site_photo_note", "deficiency_memo", "inspection_note", "approval_note"]
        for doc_index in range(1, doc_count + 1):
            category = categories[min(doc_index - 1, len(categories) - 1)]
            filename = f"{application_number.lower()}_{category}_{doc_index:02d}.txt"
            payload = (
                f"{application_number}\n"
                f"{category}\n"
                f"Ward: {prop['ward_name']}\n"
                f"City: {prop['city']}\n"
                f"Applicant: {applicant_name}\n"
                f"Generated for synthetic demo use only.\n"
            )
            documents.append({
                "document_id": str(uuid.uuid4()),
                "aggregate_type": "license",
                "aggregate_id": license_id,
                "property_id": prop["id"],
                "license_id": license_id,
                "filename": filename,
                "media_type": "text/plain",
                "size_bytes": len(payload.encode("utf-8")),
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                "uploaded_by": officer["subject"],
                "content": payload,
            })

    # dashboard metrics
    per_city = defaultdict(lambda: {"properties": 0, "licenses": 0, "draft": 0, "submitted": 0, "under_review": 0, "approved": 0, "rejected": 0, "days": []})
    for prop in properties:
        per_city[prop["city"]]["properties"] += 1
    for lic in licenses:
        city = lic["city"]
        d = per_city[city]
        d["licenses"] += 1
        d[lic["status"]] += 1
        if lic["submitted_at"] and lic["decided_at"]:
            submitted = datetime.fromisoformat(lic["submitted_at"])
            decided = datetime.fromisoformat(lic["decided_at"])
            d["days"].append((decided - submitted).total_seconds() / 86400)

    synthetic_operational_metrics = []
    for city, values in per_city.items():
        average_days = round(statistics.mean(values["days"]) if values["days"] else 0, 1)
        on_time = round(100 * (sum(1 for x in values["days"] if x <= 15) / len(values["days"])) if values["days"] else 0, 1)
        synthetic_operational_metrics.append({
            "city": city,
            "open_properties": values["properties"],
            "open_licenses": values["licenses"],
            "draft_licenses": values["draft"],
            "submitted_licenses": values["submitted"],
            "under_review_licenses": values["under_review"],
            "approved_licenses": values["approved"],
            "rejected_licenses": values["rejected"],
            "avg_submission_to_decision_days": average_days,
            "on_time_decision_rate_percent": on_time,
            "profile_name": profile_name,
        })

    return {
        "properties": properties,
        "properties_v2": properties_v2,
        "licenses": licenses,
        "licenses_v2": licenses_v2,
        "workflow_events": workflow_events,
        "audit_events": audit_events,
        "documents": documents,
        "synthetic_operational_metrics": synthetic_operational_metrics,
    }


def export_profile(base_output: Path, profile_name: str, data: dict, catalog: dict, users: list[dict]):
    export_root = base_output / "exports" / profile_name
    extension_root = base_output / "recommended_extension_model" / profile_name
    export_root.mkdir(parents=True, exist_ok=True)
    extension_root.mkdir(parents=True, exist_ok=True)

    properties_api = [
        {key: row[key] for key in ["property_number", "ward_code", "address_line_1", "address_line_2", "city", "district", "state", "postal_code", "geo_lat", "geo_lng", "status", "use_type", "owner_name", "owner_contact", "assessment_zone", "remarks"]}
        for row in data["properties"]
    ]

    licenses_api_plan = [
        {
            "application_number": row["application_number"],
            "property_number": row["property_number"],
            "license_type": row["license_type"],
            "applicant_name": row["applicant_name"],
            "applicant_contact": row["applicant_contact"],
            "notes": row["notes"],
            "target_status": row["status"],
            "transition_path": row["transition_path"],
            "assignee_username": row["assignee_username"],
            "ward_code": row["ward_code"],
            "ward_name": row["ward_name"],
            "city": row["city"],
        }
        for row in data["licenses"]
    ]

    ward_rows = []
    for ward in catalog["pune_wards"] + catalog["mumbai_wards"]:
        ward_rows.append({key: ("; ".join(map(str, value)) if isinstance(value, list) else ", ".join(map(str, value)) if isinstance(value, tuple) else value) for key, value in ward.items()})

    write_jsonl(export_root / "properties_api.jsonl", properties_api)
    write_jsonl(export_root / "licenses_api_plan.jsonl", licenses_api_plan)
    write_csv(export_root / "ward_metadata.csv", ward_rows)
    write_csv(export_root / "user_profiles.csv", [
        {"subject": u["subject"], "username": u["username"], "email": u["email"], "department": u["department"], "active": u["active"], "roles": ";".join(u["roles"])}
        for u in users
    ])

    keycloak_seed = {
        "realm": "municipal",
        "users": [
            {
                "username": u["username"],
                "enabled": True,
                "email": u["email"],
                "attributes": {"department": [u["department"]]},
                "realmRoles": u["roles"],
                "credentials": [{"type": "password", "value": "ChangeMe!2026", "temporary": True}],
            }
            for u in users
        ],
    }
    write_json(export_root / "keycloak_users_seed.json", keycloak_seed)
    write_json(export_root / "dashboard_metrics.json", {
        "public_reference_metrics": catalog["public_reference_metrics"],
        "synthetic_operational_metrics": data["synthetic_operational_metrics"],
        "generated_profile": profile_name,
    })
    write_csv(export_root / "workflow_events.csv", data["workflow_events"])
    write_csv(export_root / "audit_events.csv", data["audit_events"])
    write_json(export_root / "import_manifest.json", {
        "profile_name": profile_name,
        "property_count": len(data["properties"]),
        "license_count": len(data["licenses"]),
        "document_stub_count": min(120, len(data["documents"])),
        "workflow_event_count": len(data["workflow_events"]),
        "audit_event_count": len(data["audit_events"]),
        "note": "Use integration/import_via_api.py so encryption, audit logging and workflow rules are preserved.",
    })

    docs_dir = export_root / "sample_documents"
    docs_dir.mkdir(exist_ok=True)
    for doc in data["documents"][:120]:
        (docs_dir / doc["filename"]).write_text(doc["content"], encoding="utf-8")

    write_csv(extension_root / "properties_v2.csv", data["properties_v2"])
    write_csv(extension_root / "licenses_v2.csv", data["licenses_v2"])
    write_csv(extension_root / "documents_v2_manifest.csv", [{key: value for key, value in row.items() if key != "content"} for row in data["documents"]])

    inspections = []
    payments = []
    for row in data["licenses_v2"]:
        if row["requires_site_inspection"]:
            inspections.append({
                "inspection_id": str(uuid.uuid4()),
                "license_id": row["license_id"],
                "application_number": row["application_number"],
                "inspection_type": random.choice(["desk_review", "site_visit", "joint_inspection"]),
                "scheduled_date": (datetime.fromisoformat(row["created_at"]) + timedelta(days=random.randint(2, row["sla_days"]))).date().isoformat(),
                "inspection_result": random.choices(["pending", "satisfactory", "conditional", "deficient"], weights=[0.25, 0.46, 0.15, 0.14], k=1)[0],
                "assigned_team": random.choice(["ward_engineering", "license_inspection", "health_section", "fire_referral_cell"]),
                "remarks": row["remarks"],
            })
        payments.append({
            "payment_id": str(uuid.uuid4()),
            "license_id": row["license_id"],
            "application_number": row["application_number"],
            "fee_amount_inr": row["fee_amount_inr"],
            "payment_status": row["payment_status"],
            "payment_channel": random.choices(["online_pg", "bank_counter", "cash_counter"], weights=[0.58, 0.24, 0.18], k=1)[0],
            "receipt_number": f"RCPT-{row['application_number'].split('-')[-1]}",
        })

    write_csv(extension_root / "inspections_v2.csv", inspections, fieldnames=["inspection_id","license_id","application_number","inspection_type","scheduled_date","inspection_result","assigned_team","remarks"])
    write_csv(extension_root / "payments_v2.csv", payments)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="developer_seed", help="Profile name from municipal_seed_profiles.json")
    parser.add_argument("--output-dir", default="../generated", help="Output folder for generated seed data")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    catalog = load_json(script_dir / "municipal_seed_catalog.json")
    profiles = load_json(script_dir / "municipal_seed_profiles.json")
    if args.profile not in profiles:
        raise SystemExit(f"Unknown profile {args.profile!r}. Available profiles: {', '.join(sorted(profiles))}")

    output_dir = Path(args.output_dir).resolve()
    users = build_users(catalog["pune_wards"], catalog["mumbai_wards"])
    data = build_profile(args.profile, profiles[args.profile], catalog, users, args.seed)

    export_profile(output_dir, args.profile, data, catalog, users)
    print(json.dumps({
        "profile": args.profile,
        "output_dir": str(output_dir),
        "property_count": len(data["properties"]),
        "license_count": len(data["licenses"]),
        "document_count": len(data["documents"]),
    }, indent=2))


if __name__ == "__main__":
    main()
