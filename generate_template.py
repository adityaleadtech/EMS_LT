#!/usr/bin/env python
"""
Generate Excel template with sample data
"""

import pandas as pd
import random
import os

def generate_sample_data(rows: int = 100):
    """Generate sample hierarchical data"""
    
    data = {
        'country_code': [],
        'country_name': [],
        'state_code': [],
        'state_name': [],
        'pc_district_code': [],
        'pc_district_name': [],
        'assembly_code': [],
        'assembly_name': [],
        'assembly_number': [],
        'constituency_type': [],
        'assembly_population': [],
        'block_code': [],
        'block_name': [],
        'block_type': [],
        'panchayat_ward_code': [],
        'panchayat_ward_name': [],
        'ward_number': [],
        'ward_type': [],
        'pincode': [],
        'booth_code': [],
        'booth_name': [],
        'booth_number': [],
        'address': []
    }
    
    # Sample data
    countries = ['IN', 'US', 'UK']
    country_names = ['India', 'United States', 'United Kingdom']
    
    states = {
        'IN': ['MH', 'KA', 'TN', 'UP', 'GJ'],
        'US': ['CA', 'NY', 'TX', 'FL', 'IL'],
        'UK': ['ENG', 'SCO', 'WAL', 'NIR']
    }
    
    state_names = {
        'IN': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'Gujarat'],
        'US': ['California', 'New York', 'Texas', 'Florida', 'Illinois'],
        'UK': ['England', 'Scotland', 'Wales', 'Northern Ireland']
    }
    
    constituency_types = ['General', 'SC', 'ST']
    block_types = ['Urban', 'Rural']
    ward_types = ['Urban', 'Rural']
    
    for i in range(rows):
        country_idx = random.randint(0, len(countries) - 1)
        country = countries[country_idx]
        country_name = country_names[country_idx]
        
        state_idx = random.randint(0, len(states[country]) - 1)
        state = states[country][state_idx]
        state_name = state_names[country][state_idx]
        
        pc_num = random.randint(1, 20)
        assembly_num = random.randint(1, 10)
        block_num = random.randint(1, 5)
        ward_num = random.randint(1, 5)
        booth_num = random.randint(1, 3)
        
        data['country_code'].append(country)
        data['country_name'].append(country_name)
        data['state_code'].append(state)
        data['state_name'].append(state_name)
        data['pc_district_code'].append(f"{state}_{pc_num:02d}")
        data['pc_district_name'].append(f"District {pc_num}")
        data['assembly_code'].append(f"{state}_{pc_num:02d}_AC{assembly_num}")
        data['assembly_name'].append(f"Assembly {assembly_num}")
        data['assembly_number'].append(assembly_num)
        data['constituency_type'].append(random.choice(constituency_types))
        data['assembly_population'].append(str(random.randint(50000, 200000)))
        data['block_code'].append(f"B{block_num}")
        data['block_name'].append(f"Block {block_num}")
        data['block_type'].append(random.choice(block_types))
        data['panchayat_ward_code'].append(f"W{ward_num}")
        data['panchayat_ward_name'].append(f"Ward {ward_num}")
        data['ward_number'].append(ward_num)
        data['ward_type'].append(random.choice(ward_types))
        data['pincode'].append(str(random.randint(100000, 999999)))
        data['booth_code'].append(f"BOOTH{booth_num}")
        data['booth_name'].append(f"Booth {booth_num}")
        data['booth_number'].append(booth_num)
        data['address'].append(f"Address {i+1}, Area {random.randint(1, 100)}")
    
    df = pd.DataFrame(data)
    return df

def generate_template():
    """Generate empty template with headers only"""
    df = pd.DataFrame({
        'country_code': [''],
        'country_name': [''],
        'state_code': [''],
        'state_name': [''],
        'pc_district_code': [''],
        'pc_district_name': [''],
        'assembly_code': [''],
        'assembly_name': [''],
        'assembly_number': [''],
        'constituency_type': [''],
        'assembly_population': [''],
        'block_code': [''],
        'block_name': [''],
        'block_type': [''],
        'panchayat_ward_code': [''],
        'panchayat_ward_name': [''],
        'ward_number': [''],
        'ward_type': [''],
        'pincode': [''],
        'booth_code': [''],
        'booth_name': [''],
        'booth_number': [''],
        'address': ['']
    })
    return df

if __name__ == "__main__":
    # Generate empty template
    template = generate_template()
    template.to_excel('template_empty.xlsx', index=False)
    print("✅ Generated template_empty.xlsx")
    
    # Generate sample data with 100 rows
    sample_data = generate_sample_data(100)
    sample_data.to_excel('sample_data_100.xlsx', index=False)
    print("✅ Generated sample_data_100.xlsx with 100 records")
    
    # Generate sample data with 1000 rows
    sample_data = generate_sample_data(1000)
    sample_data.to_excel('sample_data_1000.xlsx', index=False)
    print("✅ Generated sample_data_1000.xlsx with 1000 records")