from youtubesearchpython import VideosSearch
import json
import os

def harvest_youtube_tactics(limit=5):
    keywords = ["tactics valorant", "win a valorant game", "best tactic in valorant"]
    all_results = []
    
    print(f"--- AURORA YouTube Tactics Harvester ---")
    
    for kw in keywords:
        print(f"Searching for: '{kw}'...")
        videosSearch = VideosSearch(kw, limit=limit)
        results = videosSearch.result()
        
        for video in results['result']:
            all_results.append({
                'id': video['id'],
                'title': video['title'],
                'url': f"https://www.youtube.com/watch?v={video['id']}",
                'duration': video['duration'],
                'views': video['viewCount']['short'],
                'keyword': kw
            })
            
    # Remove duplicates
    unique_results = {v['id']: v for v in all_results}.values()
    
    output_file = 'youtube_raw_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(unique_results), f, indent=4, ensure_ascii=False)
        
    print(f"Successfully harvested {len(unique_results)} videos to {output_file}")
    return output_file

if __name__ == "__main__":
    harvest_youtube_tactics()
