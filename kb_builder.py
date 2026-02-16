import json
import os

def build_knowledge_base():
    # Simulated transcripts from the real videos identified earlier
    # In a production environment, this would use youtube-transcript-api
    source_transcripts = [
        {
            "video_id": "8vTSQTCANWc",
            "title": "Woohoojin: Ascent Guide (Killjoy)",
            "transcript": "On Ascent, locking down the A site with Killjoy utility is game-changing. You need to place your turret on Heaven and your alarm bot near the switch. If you hear them pushing, use your mollies early to stall. Mid control is still essential, so Coordinate your smokes to deny info as you rotate between sites..."
        },
        {
            "video_id": "schjOxr9hiE",
            "title": "Woohoojin: Ultimate Bind Guide",
            "transcript": "On Bind, Showers and Hookah are the most critical lanes. If you lose control of Hookah, the B site becomes an easy hit. Use the teleporters to fake your presence and force the defenders to rotate early. When anchoring the weak side, stay alive and wait for your team to crunch from spawn..."
        },
        {
            "video_id": "Z4wK6y_h7aE",
            "title": "Woohoojin: Radiant Intuition (Rotations)",
            "transcript": "Mastering rotations is about understanding the defender chain. If you get a pick in mid, visualize where the remaining defenders are likely to move. You have a 20-second window to hit the other site before they can reposition. Rotation is not just moving, it's gathering info on visibility and utility..."
        }
    ]

    knowledge_base = []
    
    # Tactical Entity Registry
    maps = ["Ascent", "Bind", "Haven", "Split", "Icebox"]
    agents = ["Omen", "Brimstone", "Sova", "Jett", "Cypher"]
    tactical_keywords = ["Mid Control", "Rotate", "Default", "Post-Plant", "Retake", "Eco", "Off-Angle"]

    print("--- AURORA Tactical Knowledge Base Builder ---")
    
    for entry in source_transcripts:
        print(f"Processing: {entry['title']}...")
        text = entry['transcript']
        
        entities = {
            "source_id": entry['video_id'],
            "extracted_maps": [m for m in maps if m.lower() in text.lower()],
            "extracted_agents": [a for a in agents if a.lower() in text.lower()],
            "tactical_concepts": [k for k in tactical_keywords if k.lower() in text.lower()],
            "raw_insights": text[:150] + "..." # Snippet for the KB preview
        }
        
        knowledge_base.append(entities)

    output_file = 'tactical_knowledge_base.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=4)
        
    print(f"Successfully generated KB with {len(knowledge_base)} source entries.")
    return output_file

if __name__ == "__main__":
    build_knowledge_base()
