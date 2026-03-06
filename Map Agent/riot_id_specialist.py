class RiotIDSpecialist:
    def __init__(self):
        # Official Valorant Map UUIDs (Source: valorant-api.com)
        self.map_registry = {
            "ASCENT": "7eaecc1b-4337-bbf6-6ab9-04b8f06b3319",
            "BIN": "2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba", # Catching variant
            "BIND": "2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba",
            "HAVEN": "2bee0dc9-4ffe-519b-1cbd-7fbe763a6047",
            "SPLIT": "d960549e-485c-e861-8d71-aa9d1aed12a2",
            "ICEBOX": "e2ad5c54-4114-a870-9641-8ea21279579a",
            "BREEZE": "2fb9a4fd-4777-e1ad-7143-d0aa0342f0d1",
            "FRACTURE": "b5294d57-4d69-55a8-18c5-534e27bb5062",
            "PEARL": "fd2673d9-4171-bc6e-ee8a-ed45ea4e517a",
            "LOTUS": "d4f51152-431a-7b3b-8211-1939884a44b7",
            "SUNSET": "9258ff4a-44a2-938a-36fb-a988d4474744",
            "ABYSS": "2181751d-44a2-938a-36fb-a988d4474744",
            "RANGE": "ee613ee9-28b7-4beb-9666-08db13bb2244",
            "DISTRICT": "690b3edc-4c1a-b09d-3130-a99c459ca340", # TDM
            "KASBAH": "12452a9d-48c3-0b02-e7ad-019572be278e", # TDM
            "PIAZZA": "de7d23fc-46c5-4424-df3d-6d8856ce99ea"   # TDM
        }

    def get_map_uuid(self, map_name):
        """
        Returns the official Riot UUID for a given map name.
        """
        if not map_name:
            return "UNKNOWN"
            
        clean_name = map_name.upper().strip()
        
        # Exact match
        if clean_name in self.map_registry:
            return self.map_registry[clean_name]
            
        # Partial match (e.g. "Map: Bind" -> "BIND")
        for key in self.map_registry:
            if key in clean_name:
                return self.map_registry[key]
                
        return "UNKNOWN"

if __name__ == "__main__":
    specialist = RiotIDSpecialist()
    print(specialist.get_map_uuid("Bind"))
