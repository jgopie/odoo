# Trailer Import ReadME

## How to use

# RTW Trailer Import Wizard

The **RTW Trailer Import Wizard** allows users to bulk import trailers into the system from a CSV file. It supports creating new trailers, updating existing ones, or a combination of both.

---

## Model

**Model Name:** `rtw_information.trailer.import.wizard`  
**Type:** Transient (Wizard)  
**Purpose:** Temporary interface to handle bulk CSV imports of trailers.

---

## Fields

| Field Name      | Type       | Description |
|-----------------|------------|------------|
| `import_file`   | Binary     | The CSV file containing trailer data. Required. |
| `file_name`     | Char       | Name of the uploaded file. Auto-filled. |
| `import_mode`   | Selection  | Determines import behavior: <br>- `create_only` – only create new records <br>- `update_existing` – only update existing records <br>- `create_update` – create new and update existing |
| `sample_data`   | Text       | Sample CSV content and instructions. Read-only. |

---

## Buttons / Actions

### Import Trailers
- **Method:** `action_import_trailers()`
- **Function:** Processes the uploaded CSV and creates or updates trailer records based on `import_mode`.
- **Returns:** Notification message indicating how many records were created, updated, or failed.

### Download Sample CSV
- **Method:** `action_download_sample()`
- **Function:** Generates a downloadable CSV sample for users to understand the correct format.
- **Implementation:** Creates an attachment linked to the current user and provides a URL for download.

---

## CSV Format

| Column Name            | Required | Type / Format                                | Notes |
|------------------------|----------|---------------------------------------------|-------|
| `license_plate`        | Yes      | String                                      | Unique identifier for the trailer. |
| `is_rigid`             | Yes      | Boolean (`True` / `False`)                  | Indicates if the trailer is rigid. |
| `manufacturer`         | No       | String                                      | Name of the trailer manufacturer. Leave blank if unknown. |
| `contractor`           | No       | Selection (`sktl`, `ldst`, `crb`)          | Contractor associated with the trailer. |
| `compartment_capacities` | Yes     | JSON Array `[capacity1, capacity2, ...]`   | List of compartment capacities in liters. Must be valid JSON array. |

**Example CSV:**

```csv
license_plate,is_rigid,manufacturer,contractor,compartment_capacities
TRL001,True,Volvo,sktl,"[25000, 30000, 25000]"
TRL002,False,Mercedes,ldst,"[40000, 35000]"
TRL003,True,Scania,crb,"[20000, 20000, 20000, 15000]"
```

---

## Import Logic

1. The CSV is read using `csv.DictReader`. Supports **comma-separated** or **tab-separated** files.
2. Each row is validated:
   - `license_plate` must be present.
   - `compartment_capacities` must be a valid JSON array.
   - Contractor must be a valid selection if provided.
3. Depending on `import_mode`:
   - `create_only`: creates new trailers; errors on duplicates.
   - `update_existing`: updates existing trailers; errors on missing records.
   - `create_update`: creates new and updates existing trailers.
4. Compartments are created or updated according to the JSON array provided.
5. Errors are collected and reported to the user with row numbers.

---

## Notes / Recommendations

- Use **empty strings** instead of `null` for optional fields.
- Extra quotes around JSON arrays (`"""[25000, 30000]"""`) should be avoided; the wizard will strip single wrapping quotes automatically.
- Supports **Excel exports**, but ensure they are saved as CSV (comma or tab-delimited).

