# **Title: TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**


## **1. Methodology**
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Topsis_steps.png/800px-Topsis_steps.png" width="80%" height="80%">

**TOPSIS Method Steps:**
1. Construct the decision matrix  
2. Normalize the decision matrix  
3. Apply weights to normalized matrix  
4. Determine ideal best and ideal worst solutions  
5. Calculate distance from ideal best and worst  
6. Compute TOPSIS score and rank alternatives  


---

## **2. Description**
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) is a multi-criteria decision-making (MCDM) technique.  
This project provides:

- A **Python package** for TOPSIS (published on PyPI)
- A **web-based interface** to upload CSV/XLSX files
- Automatic calculation of TOPSIS scores and rankings
- Easy-to-use UI for students and analysts  

The system ranks alternatives based on their closeness to the ideal solution using user-defined **weights** and **impacts**.


---

## **3. Input / Output**

### **Input**
- Dataset file (`.csv` or `.xlsx`)
- Weights (comma-separated, e.g. `1,2,1,1`)
- Impacts (`+` or `-`, e.g. `+,+,-,+`)
- Email ID (for result delivery)

### **Output**
- Ranked alternatives
- TOPSIS score for each alternative
- Downloadable result file

<img src="https://user-images.githubusercontent.com/7460892/207004091-8f67548d-50ac-49c3-b7cb-ef8ec18a6491.png" width="40%" height="40%">


---

## **4. Live Link**
🔗 **Web Application:**  
https://loveyyyy99.pythonanywhere.com  

🔗 **PyPI Package:**  
https://pypi.org/project/topsis-lovepreet-102303335/


---

## **5. Screenshot of the Interface**
<img src="https://user-images.githubusercontent.com/7460892/207004468-57fc5284-f747-4b93-9bb7-2ff7f1032837.png" width="50%" height="50%">


---

## **6. Installation (PyPI)**
```bash
pip install topsis-lovepreet-102303335
