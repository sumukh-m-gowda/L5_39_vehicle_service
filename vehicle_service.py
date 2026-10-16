"""Vehicle service record manager.

Tracks service jobs per vehicle, calculates costs, and saves/loads records.
"""

import hashlib
import json
import os
import shutil
from datetime import date

SERVICE_RATES = {
    "Oil Change": 1500,
    "Wheel Alignment": 800,
    "General": 2500,
    "Brake Check": 1200,
}

SERVICE_RECORDS = {}


def add_service(vehicle_no, service_type="General", history=None):
    """Add a service job for a vehicle and return the updated history list."""
    if history is None:
        history = []
    cost = SERVICE_RATES.get(service_type, 0)
    entry = {"type": service_type, "cost": cost, "date": str(date.today())}
    SERVICE_RECORDS.setdefault(vehicle_no, []).append(entry)
    history.append(vehicle_no)
    return history


def cancel_service(vehicle_no, service_type):
    """Cancel all jobs of a given type for a vehicle.

    Returns True if at least one job was removed, otherwise False.
    """
    try:
        jobs = SERVICE_RECORDS[vehicle_no]
    except KeyError:
        print("No records for", vehicle_no)
        return False
    remaining = [job for job in jobs if job["type"] != service_type]
    SERVICE_RECORDS[vehicle_no] = remaining
    return len(remaining) < len(jobs)


def get_total_cost(vehicle_no):
    """Return the total cost of all services for a vehicle."""
    return sum(job["cost"] for job in SERVICE_RECORDS.get(vehicle_no, []))


def job_card_id(vehicle_no):
    """Return a short job card ID derived from the vehicle number."""
    return hashlib.sha256(vehicle_no.encode("utf-8")).hexdigest()[:8]


def busiest_vehicle():
    """Return the vehicle with the most jobs, or None if there are no records."""
    if not SERVICE_RECORDS:
        return None
    return max(SERVICE_RECORDS, key=lambda vehicle: len(SERVICE_RECORDS[vehicle]))


def save_records(file_name="services.json"):
    """Save all service records to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(SERVICE_RECORDS, file, indent=2)


def load_records(file_name="services.json"):
    """Load service records from a JSON file and return them."""
    with open(file_name, encoding="utf-8") as file:
        return json.load(file)


def backup_records(folder, file_name="services.json"):
    """Copy the records file into a backup folder (no shell commands used)."""
    os.makedirs(folder, exist_ok=True)
    return shutil.copy2(file_name, folder)


def main():
    """Run the demo."""
    add_service("KA01AB1234", "Oil Change")
    add_service("KA01AB1234", "Wheel Alignment")
    add_service("KA05XY9876")
    add_service("KA03MN4455", "Brake Check")
    cancel_service("KA05XY9876", "Brake Check")
    cancel_service("KA09ZZ0001", "General")
    cancel_service("KA03MN4455", "Brake Check")
    print("Total for KA01AB1234:", get_total_cost("KA01AB1234"))
    print("Total for KA05XY9876:", get_total_cost("KA05XY9876"))
    print("Job card for KA01AB1234:", job_card_id("KA01AB1234"))
    save_records()
    loaded = load_records()
    print("Vehicles on file:", len(loaded), "| busiest vehicle:", busiest_vehicle())


if __name__ == "__main__":
    main()