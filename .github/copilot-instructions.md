# AI Coding Agent Instructions for FINO Stability Analysis Codebase

## Overview
This codebase is focused on analyzing high-resolution data from the FINO1 platform. The primary goal is to process and analyze `.txt` files containing 10Hz data. The code is structured to:

- Read and process data files from a specified directory.
- Use Python libraries like `pandas` and `numpy` for data manipulation.
- Follow a modular approach for scalability and maintainability.

## Key Files and Directories
- **`read_fino1.ipynb`**: The main Jupyter Notebook for data processing. It demonstrates how to load and process `.txt` files from the `D:/FINO1Data/10Hz` directory.
- **Data Directory**: The code expects high-resolution data files in the `D:/FINO1Data/10Hz` directory. Ensure this path is correctly set before running the code.

## Developer Workflows
### Running the Notebook
1. Open `read_fino1.ipynb` in VS Code.
2. Ensure the required Python environment is activated.
3. Execute the cells sequentially to process the data files.

### Debugging
- Use `print()` statements to inspect intermediate variables.
- Check the `df` DataFrame after loading files to ensure data integrity.

### Testing
- Currently, there are no automated tests. Validate the output manually by inspecting the processed DataFrame.

## Project-Specific Conventions
- **File Handling**: The code uses `glob` to locate `.txt` files in the specified directory. Ensure the directory contains valid `.txt` files.
- **DataFrames**: All data processing is done using `pandas` DataFrames. Familiarity with `pandas` operations is essential.
- **Hardcoded Paths**: The directory path (`D:/FINO1Data/10Hz`) is hardcoded. Update this path if the data is stored elsewhere.

## External Dependencies
- **Python Libraries**:
  - `numpy`
  - `pandas`
  - `glob`
- Ensure these libraries are installed in your Python environment.

## Examples
### Loading Data Files
```python
high_res_folder_name = 'D:/FINO1Data/10Hz'
files = glob(os.path.join(high_res_folder_name, '/*.txt'))

for file in files:
    file_path = os.path.join(high_res_folder_name, file)
    df = pd.read_csv(file_path)
    print(df.head())
```

### Inspecting Data
```python
print(df.info())
print(df.describe())
```

## Notes
- Update the hardcoded paths to match your local setup.
- Ensure `.txt` files are formatted correctly for `pandas.read_csv()` to parse them without errors.

---
This document is a starting point. Update it as the project evolves to reflect new patterns and workflows.