# Tripitaka.online Nikaya Configuration
# Based on manual exploration of the website structure

NIKAYA_RANGES = {
    "digha": {
        "name": "දීඝ නිකාය",
        "name_en": "Dīgha Nikāya", 
        "start": 17,
        "end": 264,  # Just before Majjhima starts
        "description": "Long Discourses"
    },
    "majjhima": {
        "name": "මජ්ඣිම නිකාය",
        "name_en": "Majjhima Nikāya",
        "start": 265,
        "end": 979,  # Just before Samyutta starts
        "description": "Middle Length Discourses"
    },
    "samyutta": {
        "name": "සංයුත්ත නිකාය", 
        "name_en": "Saṃyutta Nikāya",
        "start": 980,
        "end": 1172,  # Just before Khuddaka starts
        "description": "Connected Discourses"
    },
    "khuddaka": {
        "name": "ඛුද්දක නිකාය",
        "name_en": "Khuddaka Nikāya", 
        "start": 1173,
        "end": 5756,  # Just before Anguttara starts
        "description": "Minor Collection"
    },
    "anguttara": {
        "name": "අංගුත්තර නිකාය",
        "name_en": "Aṅguttara Nikāya",
        "start": 5757,
        "end": 15702,  # Maximum sutta number
        "description": "Numerical Discourses"
    }
}

def get_nikaya_info(sutta_number: int):
    """
    Get the Nikaya information for a given sutta number
    
    Args:
        sutta_number: The sutta number to look up
        
    Returns:
        dict: Nikaya information or None if not found
    """
    for nikaya_key, nikaya_info in NIKAYA_RANGES.items():
        if nikaya_info["start"] <= sutta_number <= nikaya_info["end"]:
            return {
                "key": nikaya_key,
                **nikaya_info
            }
    return None

def get_all_nikaya_ranges():
    """
    Get all Nikaya ranges for bulk scraping
    
    Returns:
        dict: All Nikaya configurations
    """
    return NIKAYA_RANGES.copy()

def estimate_total_suttas():
    """
    Estimate total number of suttas across all Nikayas
    
    Returns:
        int: Estimated total suttas
    """
    total = 0
    for nikaya_info in NIKAYA_RANGES.values():
        range_size = nikaya_info["end"] - nikaya_info["start"] + 1
        total += range_size
    return total

def print_nikaya_summary():
    """Print a summary of all Nikaya ranges"""
    print("📚 TRIPITAKA.ONLINE STRUCTURE:")
    print("=" * 60)
    
    total_suttas = 0
    for key, info in NIKAYA_RANGES.items():
        range_size = info["end"] - info["start"] + 1
        total_suttas += range_size
        
        print(f"🔸 {info['name']} ({info['name_en']})")
        print(f"   Range: {info['start']:,} - {info['end']:,}")
        print(f"   Count: ~{range_size:,} suttas")
        print(f"   Description: {info['description']}")
        print()
    
    print(f"📊 TOTAL ESTIMATED SUTTAS: ~{total_suttas:,}")
    print("=" * 60)

if __name__ == "__main__":
    print_nikaya_summary()