# **Title: TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**


## **1. Methodology**
<img width="262" height="193" alt="images" src="https://github.com/user-attachments/assets/0ea6b0bc-b868-46e2-8e4b-1d49556f2700" />

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

- A **web-based interface** to upload CSV/XLSX files
- Automatic calculation of TOPSIS scores and rankings
- Easy-to-use UI for students and analysts  

The system ranks alternatives based on their closeness to the ideal solution using user-defined **weights** and **impacts**.


---

## **3. Input / Output**

### **Input**
- Dataset file (`.csv` or `.xlsx`)
- Weights (comma-separated, e.g. `1,2,2,1,1`)
- Impacts (`+` or `-`, e.g. `+,+,+,+,+`)
- Email ID (for result delivery)
<img width="452" height="300" alt="Screenshot 2026-01-19 181241" src="https://github.com/user-attachments/assets/92225251-21c8-4b7a-a317-870975ded2f8" />

### **Output**
- Ranked alternatives
- TOPSIS score for each alternative
- Downloadable result file
<img width="724" height="207" alt="Screenshot 2026-01-19 182204" src="https://github.com/user-attachments/assets/30181c65-20bb-4e1e-9ebe-ac0639d54dba" />

---

## **4. Live Link**
🔗 **Web Application:**  
https://topsis-tr8s.vercel.app/ 

🔗 **PyPI Package:**  
https://pypi.org/project/topsis-lovepreet-102303335/


---

## **5. Screenshot of the Interface**
<img width="1247" height="892" alt="Screenshot 2026-01-19 182644" src="https://github.com/user-attachments/assets/7039aba7-b88e-4f99-afa1-360bbbc7aa4c" />

---

## **6. Installation (PyPI)**
```bash
pip install topsis-lovepreet-102303335
