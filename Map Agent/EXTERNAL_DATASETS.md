# 📂 External Valorant Datasets for Training

> [!WARNING]
> Direct dataset URLs on Kaggle and Roboflow can go dead quickly. Use the **search terms** below on each platform to find current datasets.

---

## 📊 Kaggle Datasets

Go to **[kaggle.com/datasets](https://www.kaggle.com/datasets)** and search:

| Search Term | What You'll Get |
|---|---|
| `valorant image dataset structured` | 8,247 labeled images (maps, agents, weapons, abilities) |
| `valorant agent detection challenge` | 2,825 gameplay frames with agent bboxes |
| `valorant VCT esports detection` | Pro scene footage with object annotations |

### How to Download
1. Open the dataset page on Kaggle.
2. Click the "Download (All)" button (requires a free Kaggle account).
3. Extract the ZIP file — you'll find images in `/images/` or categorized folders.

---

## 👁️ Roboflow Universe Datasets

Go to **[universe.roboflow.com](https://universe.roboflow.com)** and search:

| Search Term | What You'll Get |
|---|---|
| `valorant enemy` | 2,567 tagged gameplay images |
| `Valorant Object Detection` | 10k+ images, 77 classes (agents, items) |
| `VALORANT REMATCH` | 121 quick-access detection images |

### How to Download from Roboflow
1. Open the dataset on Roboflow Universe.
2. Click **"Download Dataset"**.
3. Choose format: **JPG (images only)** — you just need the images for Teachable Machine.
4. A ZIP will download with all images inside.

---

## 🛠️ Using with Teachable Machine
1. Download the images and unzip them.
2. Sort them manually into folders by class (e.g., `Ascent`, `Bind`, `Haven`).
3. Upload each folder as a separate **Class** in Teachable Machine.
4. If the dataset has mixed content (agents + maps), filter out the map-related images only.
